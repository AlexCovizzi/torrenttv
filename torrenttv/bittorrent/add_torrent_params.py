from python_libtorrent import libtorrent as lt  # pylint: disable=no-name-in-module
from torrenttv.utils import compat_utils


def create_add_torrent_params(link, **kwargs):
    save_path = kwargs.get("save_path", compat_utils.path.get_download())

    if link.endswith(".fastresume"):
        # resume data file path
        params = lt.read_resume_data(open(link, "rb").read())

        return params

    if link.startswith("magnet:"):
        # magnet uri
        params = lt.parse_magnet_uri(link)
    else:
        # torrent file path
        params = lt.add_torrent_params()

        t_info = lt.torrent_info(link)
        params.ti = t_info
        # set the info_hash in the params so that it's easely accessible
        params.info_hash = t_info.info_hash()

    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t.storage_mode_sparse
    params.flags |= (
        lt.torrent_flags.duplicate_is_error | lt.torrent_flags.auto_managed)

    return params
