import re
from torrenttv.utils import ensure_str, ensure_int


def format_(value, regx, fmt, cvt, defval):
    value = ensure_str(value)
    if not fmt:
        # if no format is specified we just return the matched string
        matched = re.match(regx, value)
        if matched:
            value = matched.group(0)
    else:
        # otherwise we replace
        value = re.sub(regx, fmt, value)

    if cvt == "int":
        defval = ensure_int(defval)
        value = ensure_int(value, defval=defval)
    else:
        defval = ensure_str(defval)
        value = ensure_str(value, defval=defval)

    return value
