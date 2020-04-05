import asyncio
from python_libtorrent import libtorrent as lt
from .add_torrent_params import create_add_torrent_params
from .session_settings import create_session_settings
from .event_emitter import EventEmitter
from .torrent import Torrent
from .exceptions import (
    AddTorrentError,
    DeleteFailedError,
    TorrentError,
    ReadPieceError,
)
from .events import (
    AlertEvent,
    AddTorrentEvent,
    RemoveTorrentEvent,
    DeleteFilesEvent,
    ErrorEvent,
    StateEvent,
    PausedEvent,
    ResumedEvent,
    PieceEvent,
)


class Session(EventEmitter):
    def __init__(self, **kwargs):
        super().__init__()

        settings = create_session_settings(**kwargs)
        self._loop = kwargs.get("loop", asyncio.get_event_loop())
        self._session = lt.session(settings)
        self._torrents = {}
        self._alive = False

        self._alert_handlers = {
            "add_torrent_alert": self._add_torrent_alert,
            "torrent_removed_alert": self._torrent_removed_alert,
            "torrent_deleted_alert": self._torrent_deleted_alert,
            "torrent_delete_failed_alert": self._torrent_delete_failed_alert,
            "torrent_error_alert": self._torrent_error_alert,
            "state_changed_alert": self._state_changed_alert,
            "torrent_paused_alert": self._torrent_paused_alert,
            "torrent_resumed_alert": self._torrent_resumed_alert,
            "read_piece_alert": self._read_piece_alert,
        }

    async def run(self):
        self._alive = True

        self._session.set_alert_notify(
            # we use call_soon_threadsafe since this function
            # is executed in the libtorrent thread
            lambda: self._loop.call_soon_threadsafe(self.emit, AlertEvent())
        )

        while self._alive:
            await self.event(AlertEvent(), loop=self._loop)
            alerts = self._session.pop_alerts()
            for alert in alerts:
                self._dispatch_alert(alert)

    async def shutdown(self):
        def _shutdown():
            self._alive = False

        self.loop.call_soon(_shutdown)

    async def add_torrent(self, link, **kwargs):
        params = create_add_torrent_params(link, **kwargs)
        info_hash = params.info_hash.to_bytes().hex()

        self._session.async_add_torrent(params)

        result = await self.event(AddTorrentEvent(info_hash), loop=self._loop)

        result.raise_err()

        torrent = Torrent(result.ok, loop=self._loop)
        self._torrents[info_hash] = torrent

        return torrent

    async def remove_torrent(self, torrent, delete_files=False):
        handle = torrent._handle
        delete_files_flag = 1 if delete_files else 0

        self._session.remove_torrent(handle, delete_files_flag)

        info_hash = torrent.info_hash

        self._torrents.pop(info_hash, None)

        if delete_files:
            result, delete_result = await asyncio.gather(
                self.event(RemoveTorrentEvent(info_hash), loop=self._loop),
                self.event(DeleteFilesEvent(info_hash), loop=self._loop),
                loop=self._loop,
            )

            # raise an error if libtorrent failed to
            # delete the files
            # Note: the torrent is ALWAYS removed
            delete_result.raise_err()
        else:
            result = await self.event(RemoveTorrentEvent(info_hash), loop=self._loop)

        return result.ok

    async def pause(self):
        self._session.pause()
        # wait paused event on every torrent
        await asyncio.gather(
            *[torrent.event(PausedEvent()) for torrent in self.get_torrents()],
            loop=self.loop
        )

    async def resume(self):
        self._session.resume()
        # wait resumed event on every torrent
        await asyncio.gather(
            *[torrent.event(ResumedEvent()) for torrent in self.get_torrents()],
            loop=self.loop
        )

    def get_torrent(self, info_hash):
        if isinstance(info_hash, bytes):
            info_hash = info_hash.hex()
        if len(info_hash) >= 40:
            return self._torrents.get(info_hash, None)
        else:
            for torrent_info_hash, torrent in self._torrents.items():
                if torrent_info_hash.startswith(info_hash):
                    return torrent
            return None

    def get_torrents(self):
        # maybe filter out the torrents whose handle is not valid
        return list(self._torrents.values())

    @property
    def loop(self):
        return self._loop

    @property
    def paused(self):
        return self._session.is_paused()

    @property
    def download_rate(self):
        return self._session.status().download_rate

    @property
    def upload_rate(self):
        return self._session.status().upload_rate

    @property
    def download_rate_limit(self):
        return self._session.download_rate_limit()

    @property
    def upload_rate_limit(self):
        return self._session.upload_rate_limit()

    @property
    def num_seeds(self):
        return self._session.status().num_seeds

    @property
    def num_peers(self):
        return self._session.status().num_peers

    @property
    def num_connections(self):
        return self._session.num_connections()

    @property
    def connections_limit(self):
        return self._session.max_connections()

    def set_download_rate_limit(self, limit):
        self._session.set_download_rate_limit(limit)

    def set_upload_rate_limit(self, limit):
        self._session.set_upload_rate_limit(limit)

    def set_connections_limit(self, limit):
        self._session.set_max_connections(limit)

    def _dispatch_alert(self, lt_alert):
        alert_class_name = lt_alert.__class__.__name__
        if alert_class_name not in self._alert_handlers:
            # probably emit an error or a warning here
            # (like "handler_not_found")
            pass
        else:
            handler = self._alert_handlers[alert_class_name]
            handler(lt_alert)

    def _add_torrent_alert(self, alert):
        params = alert.params
        info_hash = params.ti.info_hash() if params.ti else params.info_hash
        info_hash = info_hash.to_bytes().hex()
        if alert.error.value():
            error = AddTorrentError(alert.error)
            result = Result(err=error)
        else:
            torrent_handle = alert.handle
            result = Result(ok=torrent_handle)
        self._loop.call_soon(self.emit, AddTorrentEvent(info_hash), result)

    def _torrent_removed_alert(self, alert):
        info_hash = alert.info_hash.to_bytes().hex()
        result = Result(ok=info_hash)
        self._loop.call_soon(self.emit, RemoveTorrentEvent(info_hash), result)

    def _torrent_deleted_alert(self, alert):
        info_hash = alert.info_hash.to_bytes().hex()
        result = Result(ok=info_hash)
        self._loop.call_soon(self.emit, DeleteFilesEvent(info_hash), result)

    def _torrent_delete_failed_alert(self, alert):
        info_hash = alert.info_hash.to_bytes().hex()
        error = DeleteFailedError(alert.error, info_hash)
        result = Result(err=error)
        self._loop.call_soon(self.emit, DeleteFilesEvent(info_hash), result)

    def _torrent_error_alert(self, alert):
        info_hash = alert.handle.info_hash().to_bytes().hex()
        error = TorrentError(alert.error, info_hash)
        torrent = self.get_torrent(info_hash)
        if torrent is not None:
            self._loop.call_soon(torrent.emit, ErrorEvent(), error)

    def _state_changed_alert(self, alert):
        info_hash = alert.handle.info_hash().to_bytes().hex()
        state = str(alert.state)
        prev_state = str(alert.prev_state)
        torrent = self.get_torrent(info_hash)
        if torrent is not None:
            self._loop.call_soon(torrent.emit, StateEvent(), state, prev_state)

    def _torrent_paused_alert(self, alert):
        info_hash = alert.handle.info_hash().to_bytes().hex()
        result = Result()
        torrent = self.get_torrent(info_hash)
        if torrent is not None:
            self._loop.call_soon(torrent.emit, PausedEvent(), result)

    def _torrent_resumed_alert(self, alert):
        info_hash = alert.handle.info_hash().to_bytes().hex()
        result = Result()
        torrent = self.get_torrent(info_hash)
        if torrent is not None:
            self._loop.call_soon(torrent.emit, ResumedEvent(), result)

    def _read_piece_alert(self, alert):
        info_hash = alert.handle.info_hash().to_bytes().hex()
        error = alert.error
        piece = alert.piece
        size = alert.size
        buf = alert.buffer
        if alert.error.value():
            error = ReadPieceError(error, info_hash, piece)
            result = Result(err=error)
        else:
            result = Result(ok=(piece, size, buf))
        torrent = self.get_torrent(info_hash)
        if torrent is not None:
            self._loop.call_soon(torrent.emit, PieceEvent(piece), result)


class Result:
    def __init__(self, ok=None, err=None):
        self._ok = ok
        self._err = err

    @property
    def ok(self):
        return self._ok

    @property
    def err(self):
        return self._err

    def is_ok(self):
        return self._err is None

    def is_err(self):
        return self._err is not None

    def raise_err(self):
        if self.is_err():
            if isinstance(self._err, Exception):
                raise self.err
            else:
                raise Exception(self.err)

    def __repr__(self):
        s = self.__class__.__name__
        if self.is_ok():
            s += "'ok':" + repr(self.ok)
        else:
            s += "'err':" + repr(self.err)
        return s
