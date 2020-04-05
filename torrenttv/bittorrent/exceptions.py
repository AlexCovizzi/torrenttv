import weakref


class LtError(Exception):
    """
    Wrapper for libtorrent error
    """
    def __init__(self, error):
        self.code = error.value()
        self.message = error.message()
        self.lt_error = error
        super().__init__(self.message)


class SessionError(LtError):

    def __init__(self, error):
        super().__init__(error)


class AddTorrentError(SessionError):

    def __init__(self, error):
        super().__init__(error)


class DeleteFailedError(SessionError):

    def __init__(self, error, info_hash):
        self.info_hash = info_hash
        super().__init__(error)


class TorrentError(LtError):

    def __init__(self, error, info_hash):
        self._info_hash = info_hash
        super().__init__(error)

    @property
    def info_hash(self):
        return self._info_hash


class ReadPieceError(TorrentError):

    def __init__(self, error, info_hash, piece):
        self.piece = piece
        super().__init__(error, info_hash)
