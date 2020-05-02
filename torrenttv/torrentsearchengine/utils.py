import re


def format_search_path(base_search_path: str, query: str, whitespace_char=None) -> str:
    query = query.lower().strip()
    if whitespace_char:
        query = re.sub(r"\s+", whitespace_char, query)
    if "{query}" in base_search_path:
        path = base_search_path.format(query=query)
    else:
        path = base_search_path
    return path
