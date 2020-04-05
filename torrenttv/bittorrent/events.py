class Event(str):
    def __new__(cls, name, discriminant=None, internal=False):
        fullname = name
        if discriminant is not None:
            fullname += ":" + str(discriminant)
        if internal:
            fullname = "_" + fullname
        return super().__new__(cls, fullname)


class AlertEvent(Event):
    """
    emitted a new alert is ready to be popped
    """

    def __new__(cls):
        return super().__new__(cls, "alert", internal=True)


class AddTorrentEvent(Event):
    """
    emitted when a new torrent has been added or failed to be added
    """

    def __new__(cls, info_hash):
        return super().__new__(
            cls, "add_torrent", discriminant=info_hash, internal=True
        )


class RemoveTorrentEvent(Event):
    """
    emitted when a torrent is removed
    """

    def __new__(cls, info_hash):
        return super().__new__(
            cls, "remove_torrent", discriminant=info_hash, internal=True
        )


class DeleteFilesEvent(Event):
    """
    emitted when torrent files are deleted or failed to be deleted
    """

    def __new__(cls, info_hash):
        return super().__new__(
            cls, "delete_files", discriminant=info_hash, internal=True
        )


class ErrorEvent(Event):
    """
    emitted when an error occurs (session or torrent error)
    """

    def __new__(cls):
        return super().__new__(cls, "error", internal=False)


class StateEvent(Event):
    """
    emitted when an the state of a torrent changes
    """

    def __new__(cls):
        return super().__new__(cls, "state", internal=False)


class PausedEvent(Event):
    """
    emitted the torrent is paused
    """

    def __new__(cls):
        return super().__new__(cls, "paused", internal=False)


class ResumedEvent(Event):
    """
    emitted the torrent is resumed
    """

    def __new__(cls):
        return super().__new__(cls, "resumed", internal=False)


class PieceEvent(Event):
    """
    emitted after a piece finshed downloading
    """

    def __new__(cls, piece):
        return super().__new__(cls, "piece", discriminant=piece, internal=True)
