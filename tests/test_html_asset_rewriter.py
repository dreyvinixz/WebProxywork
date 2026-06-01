from src.html_asset_rewriter import rewrite_asset_urls, rewrite_embedded_asset_urls


def test_rewrites_relative_asset_urls_through_proxy():
    html = '<head><link rel="stylesheet" href="css/style.min.css"><script src="/js/app.js"></script></head>'

    rewritten = rewrite_asset_urls(html, "http://httpforever.com/page", "http://localhost:5000/")

    assert '<base href="http://localhost:5000/http://httpforever.com/">' in rewritten
    assert 'href="http://localhost:5000/http://httpforever.com/css/style.min.css"' in rewritten
    assert 'src="http://localhost:5000/http://httpforever.com/js/app.js"' in rewritten


def test_keeps_https_and_special_urls_unchanged():
    html = (
        '<script src="https://cdn.example.com/app.js"></script>'
        '<a href="#section">Anchor</a>'
        '<a href="mailto:test@example.com">Email</a>'
    )

    rewritten = rewrite_asset_urls(html, "http://example.com", "http://localhost:5000")

    assert 'src="https://cdn.example.com/app.js"' in rewritten
    assert 'href="#section"' in rewritten
    assert 'href="mailto:test@example.com"' in rewritten


def test_rewrites_absolute_http_links_through_proxy():
    html = '<a href="http://example.org/path?q=1">Example</a>'

    rewritten = rewrite_asset_urls(html, "http://example.com", "http://localhost:5000")

    assert 'href="http://localhost:5000/http://example.org/path?q=1"' in rewritten


def test_rewrites_relative_assets_to_absolute_origin_without_proxy_base():
    html = '<head><link rel="stylesheet" href="css/style.min.css"></head>'

    rewritten = rewrite_asset_urls(html, "http://httpforever.com/page", "")

    assert '<base href="http://httpforever.com/">' in rewritten
    assert 'href="http://httpforever.com/css/style.min.css"' in rewritten
    assert "http://httpforever.com/http://httpforever.com" not in rewritten


def test_rewrites_relative_asset_urls_inside_javascript():
    js = 'skel.init({global:{href:"css/style.min.css"},wide:{href:"css/style-wide.min.css"}});'

    rewritten = rewrite_embedded_asset_urls(js, "http://httpforever.com/", "http://localhost:5000")

    assert '"http://localhost:5000/http://httpforever.com/js/css/style.min.css"' not in rewritten
    assert '"http://localhost:5000/http://httpforever.com/css/style.min.css"' in rewritten
    assert '"http://localhost:5000/http://httpforever.com/css/style-wide.min.css"' in rewritten
