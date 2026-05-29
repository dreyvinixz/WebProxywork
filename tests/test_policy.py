from pathlib import Path

from src.content_policy import ContentPolicy, normalize_domain


def test_normalize_domain_removes_port_and_www():
    assert normalize_domain("www.Example.com:8080") == "example.com"


def test_policy_blocks_exact_domain(tmp_path: Path):
    config = tmp_path / "blocked.json"
    config.write_text('{"bloqueados": ["example.com"]}', encoding="utf-8")

    policy = ContentPolicy(config)

    assert policy.is_blocked("example.com")


def test_policy_blocks_domain_with_port_and_www(tmp_path: Path):
    config = tmp_path / "blocked.json"
    config.write_text('{"bloqueados": ["example.com"]}', encoding="utf-8")

    policy = ContentPolicy(config)

    assert policy.is_blocked("www.example.com:80")


def test_policy_allows_unknown_domain(tmp_path: Path):
    config = tmp_path / "blocked.json"
    config.write_text('{"bloqueados": ["example.com"]}', encoding="utf-8")

    policy = ContentPolicy(config)

    assert not policy.is_blocked("open-site.test")


def test_policy_accepts_legacy_blocked_domains_key(tmp_path: Path):
    config = tmp_path / "blocked.json"
    config.write_text('{"blocked_domains": ["example.com"]}', encoding="utf-8")

    policy = ContentPolicy(config)

    assert policy.is_blocked("www.example.com")
