from pathlib import Path

from src.text_rewriter import TextRewriter


def test_rewriter_is_case_insensitive(tmp_path: Path):
    config = tmp_path / "substitutions.json"
    config.write_text('{"merda": "droga"}', encoding="utf-8")

    rewritten, count = TextRewriter(config).rewrite("<p>MERDA acontece</p>")

    assert rewritten == "<p>droga acontece</p>"
    assert count == 1


def test_rewriter_prefers_longer_phrase(tmp_path: Path):
    config = tmp_path / "substitutions.json"
    config.write_text('{"porra": "droga", "puta merda": "puxa vida"}', encoding="utf-8")

    rewritten, count = TextRewriter(config).rewrite("<p>puta merda, que texto</p>")

    assert rewritten == "<p>puxa vida, que texto</p>"
    assert count == 1


def test_rewriter_keeps_clean_html(tmp_path: Path):
    config = tmp_path / "substitutions.json"
    config.write_text('{"idiota": "ingenuo"}', encoding="utf-8")

    rewritten, count = TextRewriter(config).rewrite("<p>conteudo comum</p>")

    assert rewritten == "<p>conteudo comum</p>"
    assert count == 0
