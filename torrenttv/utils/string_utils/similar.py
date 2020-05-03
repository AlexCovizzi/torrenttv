import difflib


def similar(str1, str2, junk_chars=None):

    def _isjunk(char):
        if not junk_chars:
            return True
        return char in junk_chars

    return difflib.SequenceMatcher(_isjunk, str1, str2).ratio()


def get_best_match(word, possibilities):
    return difflib.get_close_matches(word, possibilities, n=1)[0]


def get_close_matches(word, possibilities, limit=None):
    return difflib.get_close_matches(word, possibilities, n=limit)
