from python_libtorrent import libtorrent as lt


def create_session_settings(**kwargs):
    user_agent = kwargs.get("user_agent", "python_libtorrent/{}".format(lt.__version__))
    listen_interface = kwargs.get("listen_interface", "0.0.0.0")
    port = kwargs.get("port", 6881)
    outgoing_interface = kwargs.get("outgoing_interface", "")
    max_download_rate = kwargs.get("max_download_rate", 0)
    max_upload_rate = kwargs.get("max_upload_rate", 0)
    proxy_host = kwargs.get("proxy_host", None)
    alert_mask = lt.alert.category_t.all_categories
    settings = {
        "user_agent": user_agent,
        "listen_interfaces": "{}:{}".format(listen_interface, port),
        "download_rate_limit": int(max_download_rate),
        "upload_rate_limit": int(max_upload_rate),
        "alert_mask": alert_mask,
        "outgoing_interfaces": outgoing_interface,
    }
    if proxy_host:
        settings["proxy_hostname"] = proxy_host.split(":")[0]
        settings["proxy_type"] = lt.proxy_type_t.http
        settings["proxy_port"] = proxy_host.split(":")[1]
    return settings
