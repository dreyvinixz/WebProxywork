from src.app_factory import create_app
from src.content_policy import ContentPolicy
import src.proxy_controller as proxy_controller


def test_https_blocked_domain_returns_block_page(tmp_path, monkeypatch):
    config = tmp_path / "blocked.json"
    config.write_text('{"bloqueados": ["blocked.test"]}', encoding="utf-8")
    monkeypatch.setattr(proxy_controller, "policy", ContentPolicy(config))
    client = create_app().test_client()

    response = client.get("/https://www.blocked.test")

    assert response.status_code == 403
    assert "Acesso bloqueado" in response.get_data(as_text=True)
    assert "www.blocked.test" in response.get_data(as_text=True)


def test_https_allowed_domain_returns_invalid_request():
    client = create_app().test_client()

    response = client.get("/https://example.com")

    assert response.status_code == 400
    assert "Este proxy aceita apenas URLs HTTP." in response.get_data(as_text=True)


def test_https_subdomain_and_different_suffix_are_blocked(tmp_path, monkeypatch):
    config = tmp_path / "blocked.json"
    config.write_text('{"bloqueados": ["blocked.test"]}', encoding="utf-8")
    monkeypatch.setattr(proxy_controller, "policy", ContentPolicy(config))
    client = create_app().test_client()

    subdomain_response = client.get("/https://sub.blocked.test")
    suffix_response = client.get("/https://blocked.test.br")

    assert subdomain_response.status_code == 403
    assert suffix_response.status_code == 403
    assert "Acesso bloqueado" in subdomain_response.get_data(as_text=True)
    assert "Acesso bloqueado" in suffix_response.get_data(as_text=True)


def test_browser_proxy_mode_does_not_duplicate_origin_url():
    client = create_app().test_client()

    response = client.get("/", base_url="http://httpforever.com")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '<base href="http://httpforever.com/">' in html
    assert "http://httpforever.com/http://httpforever.com" not in html
