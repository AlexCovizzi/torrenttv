from .watch import show as watch_show
from .session import show as session_show, update as session_update
from .torrents import (
    index as torrents_index,
    show as torrents_show,
    create as torrents_create,
    update as torrents_update,
    destroy as torrents_destroy,
)
from .files import (
    index as torrent_files_index, show as torrent_files_show, update as
    torrent_files_update
)
from .search import (search, details)

__all__ = [
    "watch_show", "session_show", "session_update", "torrents_index", "torrents_show",
    "torrents_create", "torrents_update", "torrents_destroy", "torrent_files_index",
    "torrent_files_show", "torrent_files_update", "search", "details"
]
