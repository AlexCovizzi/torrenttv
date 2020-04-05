import os
from python_libtorrent import libtorrent as lt


def create_add_torrent_params(link, **kwargs):
    save_path = kwargs.get("save_path", ".")
    params = lt.add_torrent_params()
    if link.startswith("magnet:"):
        params = lt.parse_magnet_uri(link)
    else:
        ti = lt.torrent_info(link)
        params.ti = ti
        # set the info_hash in the params so that it easely accessible
        params.info_hash = ti.info_hash()
        try:
            resume_path = os.path.join(save_path, ti.name() + ".fastresume")
            params.resume_data = open(resume_path, "rb").read()
        except Exception:
            pass
    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t.storage_mode_sparse
    params.flags |= (
        lt.torrent_flags.duplicate_is_error
        | lt.torrent_flags.auto_managed
        | lt.torrent_flags.duplicate_is_error
    )

    return params
