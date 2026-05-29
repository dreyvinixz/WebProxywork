import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SUBSTITUTIONS_FILE = ROOT_DIR / "settings" / "words.json"


@dataclass(frozen=True)
class Rule:
    original: str
    replacement: str
    pattern: re.Pattern[str]


class TextRewriter:
    def __init__(self, substitutions_file: Path = DEFAULT_SUBSTITUTIONS_FILE):
        self.substitutions_file = Path(substitutions_file)
        self.rules = self._load_rules()

    def rewrite(self, html: str) -> tuple[str, int]:
        result = html
        total_replacements = 0

        for rule in self.rules:
            result, count = rule.pattern.subn(rule.replacement, result)
            total_replacements += count

        return result, total_replacements

    def _load_rules(self) -> list[Rule]:
        if not self.substitutions_file.exists():
            return []

        data = json.loads(self.substitutions_file.read_text(encoding="utf-8"))
        ordered_items = sorted(data.items(), key=lambda item: len(item[0]), reverse=True)
        return [
            Rule(original=word, replacement=replacement, pattern=_compile_pattern(word))
            for word, replacement in ordered_items
        ]


def _compile_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if re.fullmatch(r"\w+", term, flags=re.UNICODE):
        escaped = rf"\b{escaped}\b"
    return re.compile(escaped, flags=re.IGNORECASE)
