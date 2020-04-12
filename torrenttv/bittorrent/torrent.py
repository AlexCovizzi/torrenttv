import asyncio
import os
from python_libtorrent import libtorrent as lt
from .event_emitter import EventEmitter
from .events import PieceEvent, PausedEvent, ResumedEvent, ResumeDataEvent
from .file import File


class Torrent(EventEmitter):
    CHECKING_RESUME_DATA = "checking_resume_data"
    DOWNLOADING_METADATA = "downloading_metadata"
    CHECKING_FILES = "checking_files"
    DOWNLOADING = "downloading"
    FINISHED = "finished"
    SEEDING = "seeding"
    ALLOCATING = "allocating"

    def __init__(self, handle: lt.torrent_handle, loop=None):
        super().__init__()

        self._handle = handle
        self._loop = loop or asyncio.get_event_loop()
        self._files = []

    @property
    def loop(self):
        return self._loop

    @property
    def name(self) -> str:
        return self._handle.status().name

    @property
    def path(self) -> str:
        return self._handle.save_path()

    @property
    def info_hash(self) -> str:
        return self._handle.info_hash().to_bytes().hex()

    @property
    def state(self) -> str:
        return str(self._handle.status().state)

    @property
    def paused(self) -> bool:
        # NOTE: this is false if we pause the session
        return self._handle.status().paused

    @property
    def num_seeds(self) -> int:
        return self._handle.status().num_seeds

    @property
    def num_peers(self) -> int:
        return self._handle.status().num_peers

    @property
    def num_connections(self) -> int:
        return self._handle.status().num_connections

    @property
    def connections_limit(self) -> int:
        return self._handle.max_connections()

    @property
    def num_files(self) -> int:
        if not self.has_metadata():
            return 0
        return self._handle.torrent_file().num_files()

    @property
    def total(self) -> int:
        # return self.status.total  # for some reason this is missing
        if not self.has_metadata():
            return 0
        return self._handle.torrent_file().total_size()

    @property
    def total_done(self) -> int:
        return self._handle.status().total_done

    @property
    def total_wanted(self) -> int:
        return self._handle.status().total_wanted

    @property
    def total_wanted_done(self) -> int:
        return self._handle.status().total_wanted_done

    @property
    def progress(self) -> float:
        return self._handle.status().progress

    @property
    def download_rate(self) -> int:
        return self._handle.status().download_rate

    @property
    def upload_rate(self) -> int:
        return self._handle.status().upload_rate

    @property
    def num_pieces(self) -> int:
        if not self.has_metadata():
            return 0
        return self._handle.torrent_file().num_pieces()

    @property
    def piece_length(self) -> int:
        if not self.has_metadata():
            return 0
        return self._handle.torrent_file().piece_length()

    @property
    def last_piece(self) -> int:
        if not self.has_metadata():
            return 0
        return self._handle.torrent_file().num_pieces() - 1

    @property
    def files(self):
        if len(self._files) != self.num_files:
            self._files = self._files = [
                File(self, idx) for idx in range(self.num_files)
            ]
        return self._files

    @property
    def pieces(self):
        return self._handle.status().pieces

    @property
    def download_rate_limit(self):
        return self._handle.download_limit()

    @property
    def upload_rate_limit(self):
        return self._handle.upload_limit()

    def is_valid(self):
        return self._handle.is_valid()

    def has_metadata(self):
        return self._handle.has_metadata()

    def have_piece(self, piece):
        return self._handle.have_piece(piece)

    def set_download_rate_limit(self, limit):
        self._handle.set_download_limit(limit)

    def set_upload_rate_limit(self, limit):
        self._handle.set_upload_limit(limit)

    def set_connections_limit(self, limit):
        self._handle.set_max_connections(limit)

    def set_piece_deadline(self, piece, deadline, alert_when_available=False):
        flag = 1 if alert_when_available else 0
        self._handle.set_piece_deadline(piece, deadline, flag)

    def clear_piece_deadlines(self):
        self._handle.clear_piece_deadlines()

    async def read_piece(self, piece, download=False):
        if download:
            # try to download the piece immediately
            self.set_piece_deadline(piece, 0, alert_when_available=True)
        else:
            self._handle.read_piece(piece)

        result = await self.event(PieceEvent(piece))

        result.raise_err()

        piece, size, buf = result.ok

        return (piece, size, buf)

    async def pause(self):
        self._handle.pause()

        result = await self.event(PausedEvent(), loop=self._loop)

        result.raise_err()

        return result.ok

    async def resume(self):
        self._handle.resume()

        result = await self.event(ResumedEvent(), loop=self._loop)

        result.raise_err()

        return result.ok

    async def save_resume_data(self, path=None):
        path = path or self.path
        resume_data_path = os.path.join(path, self.name + ".fastresume")

        self._handle.save_resume_data()

        result = await self.event(ResumeDataEvent(), loop=self.loop)
        result.raise_err()

        data = result.ok
        with open(resume_data_path, 'wb') as f:
            f.write(data)

        return resume_data_path

    def get_piece_size(self, piece):
        return self.info.piece_size(piece) if self.info else 0

    def get_file(self, file_idx):
        if file_idx < 0 or file_idx >= self.num_files:
            raise IndexError()
        return File(self, file_idx)

    def __eq__(self, o):
        if isinstance(o, Torrent):
            return self.info_hash == o.info_hash
        elif isinstance(o, lt.torrent_handle):
            return self._handle.info_hash() == o.info_hash()
        elif isinstance(o, lt.sha1_hash):
            return self._handle.info_hash() == o
        elif isinstance(o, bytes):
            return self.info_hash == o.hex()
        elif isinstance(o, str):
            self.info_hash == o
        else:
            return False
