import mimetypes
import weakref
import os


class File:

    def __init__(self, torrent, idx):
        self._torrent = weakref.ref(torrent)
        self._idx = idx

    @property
    def name(self):
        return self._torrent()._handle.torrent_file().files().file_name(self._idx)

    @property
    def size(self):
        return self._torrent()._handle.torrent_file().files().file_size(self._idx)

    @property
    def path(self):
        return self._torrent()._handle.torrent_file().files().file_path(self._idx)

    @property
    def mime_type(self):
        mtype, _ = mimetypes.guess_type(self.path)
        if not mtype:
            mtype = "application/octet-stream"
        return mtype

    @property
    def ext(self):
        _, f_ext = os.path.splitext(self.path)
        return f_ext

    @property
    def priority(self):
        return self._torrent()._handle.file_priority(self._idx)

    @property
    def torrent(self):
        return self._torrent()

    def is_valid(self):
        return self._torrent() is not None and self._torrent().is_valid()

    def set_priority(self, priority):
        self._torrent()._handle.file_priority(self._idx, priority)

    def map(self, offset, size):
        pr = self._torrent()._handle.torrent_file().map_file(self._idx, offset, size)
        piece = pr.piece
        start = pr.start
        length = pr.length
        return (piece, start, length)

    async def read(self, offset, size, download=False):
        if offset < 0 or offset >= self.size:
            return bytes(0)
        piece, start, length = self.map(offset, size)
        piece, size, buf = await self._torrent().read_piece(piece, download=download)
        buf = buf[start:start + length + 1]
        return buf

    async def stream(self, offset=0, chunk_size=None, buf_size=None):
        chunk_size = chunk_size or 16 * 1024
        buf_size = buf_size or self.torrent.piece_length * 8
        piece_buf_size = buf_size // self.torrent.piece_length
        last_piece = None

        # clear all deadlines previusly set,
        # we don't want them to interfere with this new stream
        self.torrent.clear_piece_deadlines()

        while True:
            piece, start, length = self.map(offset, chunk_size)
            # set deadline of the following pieces based on the download speed.
            # we set the deadline only if the piece requested is
            # different than the last piece requested,
            # this is to avoid setting the same deadline for the same pieces
            if last_piece != piece:
                last_piece = piece
                for next_piece in range(piece + 1, piece + 1 + piece_buf_size):
                    if next_piece >= self.torrent.num_pieces:
                        break
                    piece_per_second = (
                        self.torrent.download_rate / self.torrent.piece_length)
                    piece_per_second = (
                        piece_per_second if piece_per_second > 0.1 else 0.1)
                    deadline_per_piece = 1000 / piece_per_second
                    deadline = int(deadline_per_piece * (next_piece - piece))
                    self.torrent.set_piece_deadline(
                        next_piece, deadline, alert_when_available=False)
            buf = await self.read(offset, chunk_size, download=True)
            offset += len(buf)
            if not buf:
                break

            yield buf
