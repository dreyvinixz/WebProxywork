import pytest

from src.proxy_controller import build_target_from_environ, build_target_from_request, parse_target


def test_parse_accepts_http_url():
    parsed = parse_target("http://example.com/page")

    assert parsed.url == "http://example.com/page"
    assert parsed.domain == "example.com"
    assert parsed.scheme == "http"


def test_parse_accepts_https_url_for_policy_check():
    parsed = parse_target("https://www.instagram.com")

    assert parsed.url == "https://www.instagram.com"
    assert parsed.domain == "www.instagram.com"
    assert parsed.scheme == "https"


def test_parse_adds_http_when_scheme_is_missing():
    parsed = parse_target("example.com")

    assert parsed.url == "http://example.com"
    assert parsed.domain == "example.com"


def test_parse_preserves_query_string_from_proxy_request():
    parsed = parse_target("http://example.com/search", "q=teste&pagina=1")

    assert parsed.url == "http://example.com/search?q=teste&pagina=1"
    assert parsed.domain == "example.com"


def test_build_target_keeps_direct_localhost_style():
    target = build_target_from_request("neverssl.com", "localhost:5000", "5000", "")

    assert target == "neverssl.com"


def test_build_target_supports_browser_proxy_style():
    target = build_target_from_request("pagina", "example.com", "5000", "q=1")

    assert target == "http://example.com/pagina"


def test_build_target_uses_raw_uri_for_real_proxy_requests():
    target = build_target_from_environ(
        "pagina",
        {
            "RAW_URI": "http://127.0.0.1:8081/pagina?q=1",
            "HTTP_HOST": "127.0.0.1:8081",
            "SERVER_PORT": "5000",
        },
        "q=1",
    )

    assert target == "http://127.0.0.1:8081/pagina?q=1"


def test_parse_rejects_unsupported_scheme():
    with pytest.raises(ValueError):
        parse_target("ftp://example.com")


def test_parse_rejects_empty_target():
    with pytest.raises(ValueError):
        parse_target("")
