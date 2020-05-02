# pylint: disable=no-self-use,invalid-name
"""
class TestAttribute:

    def test_to_string_returns_value_as_string(self):
        val = 4
        attr = Attribute(val)
        assert attr.to_string() == "4"

    def test_to_string_returns_defval_if_value_is_none(self):
        val = None
        defval = "dflt"
        attr = Attribute(val)
        assert attr.to_string(defval=defval) == defval

    def test_to_int_returns_value_as_int(self):
        val = "4"
        attr = Attribute(val)
        assert attr.to_int() == 4

    def test_to_int_returns_defval_if_value_cannot_be_converted_to_int(self):
        val = "ciao"
        defval = 4
        attr = Attribute(val)
        assert attr.to_int(defval=defval) == defval

    def test_format_returns_the_substring_that_matches_the_regex(self):
        val = "ciao123"
        attr = Attribute(val)
        regex = r"[a-z]+"
        assert attr.format(regex) == "ciao"

    def test_format_returns_the_value_as_string_if_regex_is_empty(self):
        val = 1234
        attr = Attribute(val)
        assert attr.format("") == "1234"

    def test_format_with_fmt_returns_the_replaced_string(self):
        val = "ciao sono  alex"
        regex = r"(\s+)"
        fmt = r"_"
        attr = Attribute(val)
        assert attr.format(regex, fmt) == "ciao_sono_alex"

        val = "ciao sono alex"
        regex = r"(\w+) (\w+) (\w+)"
        fmt = r"\1:\2:\3"
        attr = Attribute(val)
        assert attr.format(regex, fmt) == "ciao:sono:alex"
"""
