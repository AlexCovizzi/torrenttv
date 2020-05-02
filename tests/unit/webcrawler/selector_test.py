import pytest
from torrenttv.webcrawler.selector import Selector


@pytest.mark.parametrize(
    "given_str, expected_selector",
    [("parent > child:focus @ text | fmt: \\1-test |regx: \\w+ |cvt: str |defval: ciao",
      {
          "pattern": "parent > child:focus",
          "attr": "text",
          "regx": "\\w+",
          "fmt": "\\1-test",
          "cvt": "str",
          "defval": "ciao"
      }),
     ("parent > child:focus | regx: \\(ciao | fmt: hey\\)+", {
         "pattern": "parent > child:focus",
         "attr": None,
         "regx": "\\(ciao",
         "fmt": "hey\\)+",
         "cvt": None,
         "defval": None
     }),
     ("parent > child:focus", {
         "pattern": "parent > child:focus",
         "attr": None,
         "regx": None,
         "fmt": None,
         "cvt": None,
         "defval": None
     })])
def test_compile_returns_expected_selector(given_str, expected_selector):
    selector = Selector.compile(given_str)
    assert selector.pattern == expected_selector["pattern"]
    assert selector.attr == expected_selector["attr"]
    assert selector.regx == expected_selector["regx"]
    assert selector.fmt == expected_selector["fmt"]
    assert selector.cvt == expected_selector["cvt"]
    assert selector.defval == expected_selector["defval"]


def test_compile_raises_value_error():
    with pytest.raises(ValueError):
        Selector.compile("parent > child:::focus")


def test_null_returns_null_selector():
    selector = Selector.null()
    assert selector.pattern == ""
    assert selector.attr is None
    assert selector.regx is None
    assert selector.fmt is None
    assert selector.cvt is None
    assert selector.defval is None
