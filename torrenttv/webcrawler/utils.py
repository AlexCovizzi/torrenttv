import re
from torrenttv.utils import type_utils


def format_(value, regx, fmt, cvt, defval):
    value = type_utils.ensure_str(value)
    if not fmt:
        # if no format is specified we just return the matched string
        matched = re.match(regx, value)
        if matched:
            value = matched.group(0)
    else:
        # otherwise we replace
        value = re.sub(regx, fmt, value)

    if cvt == "int":
        defval = type_utils.ensure_int(defval)
        value = type_utils.ensure_int(value, defval=defval)
    else:
        defval = type_utils.ensure_str(defval)
        value = type_utils.ensure_str(value, defval=defval)

    return value
