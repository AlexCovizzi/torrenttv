
def ensure_int(value, defval=None):
    defval = int(defval or 0)
    if value is None:
        return defval
    try:
        return int(value)
    except ValueError:
        return defval


def ensure_str(value, defval=None):
    defval = str(defval or "")
    if value is None:
        return defval
    try:
        return str(value)
    except ValueError:
        return defval
