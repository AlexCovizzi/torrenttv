from python_libtorrent import libtorrent as lt
from torrenttv.utils import get_os_download_path


def create_add_torrent_params(link, **kwargs):
    save_path = kwargs.get("save_path", get_os_download_path())

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

        ti = lt.torrent_info(link)
        params.ti = ti
        # set the info_hash in the params so that it's easely accessible
        params.info_hash = ti.info_hash()

    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t.storage_mode_sparse
    params.flags |= (
        lt.torrent_flags.duplicate_is_error | lt.torrent_flags.auto_managed
    )

    return params
