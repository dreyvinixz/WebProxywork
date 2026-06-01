from src.app_factory import create_app


def test_https_blocked_domain_returns_block_page():
    client = create_app().test_client()

    response = client.get("/https://www.instagram.com")

    assert response.status_code == 403
    assert "Acesso bloqueado" in response.get_data(as_text=True)
    assert "www.instagram.com" in response.get_data(as_text=True)


def test_https_allowed_domain_returns_invalid_request():
    client = create_app().test_client()

    response = client.get("/https://example.com")

    assert response.status_code == 400
    assert "Este proxy aceita apenas URLs HTTP." in response.get_data(as_text=True)


def test_browser_proxy_mode_does_not_duplicate_origin_url():
    client = create_app().test_client()

    response = client.get("/", base_url="http://httpforever.com")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '<base href="http://httpforever.com/">' in html
    assert "http://httpforever.com/http://httpforever.com" not in html
