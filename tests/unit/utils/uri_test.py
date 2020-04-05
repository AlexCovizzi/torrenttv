import pytest
from torrenttv.utils.uri import Uri


def test_http_uri():
    uri = Uri("/ciao/sono/alex?name=alex#test", scheme="http", netloc="alexcovizzi.com")

    assert uri.scheme == "http"
    assert uri.netloc == "alexcovizzi.com"
    assert uri.path == "ciao/sono/alex"
    assert uri.qs == "name=alex"
    assert uri.anchor == "test"


def test_file_uri():
    uri = Uri(path="c:\\ciao\\sono\\alex\\test.txt", scheme="file")

    assert uri.scheme == "file"
    assert not uri.netloc
    assert uri.path == "c:\\ciao\\sono\\alex\\test.txt"
    assert not uri.qs
    assert not uri.anchor


def test_data_uri():
    uri = Uri("data:application/octet-stream;base64,ciaosonoalex")

    assert uri.scheme == "data"
    assert not uri.netloc
    assert uri.path == "application/octet-stream;base64,ciaosonoalex"
    assert not uri.qs
    assert not uri.anchor
