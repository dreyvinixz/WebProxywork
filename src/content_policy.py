import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BLOCKED_FILE = ROOT_DIR / "settings" / "blocked.json"


class ContentPolicy:
    def __init__(self, blocked_file: Path = DEFAULT_BLOCKED_FILE):
        self.blocked_file = Path(blocked_file)
        self.blocked_domains = self._load_blocked_domains()

    def is_blocked(self, domain: str) -> bool:
        normalized = normalize_domain(domain)
        return normalized in self.blocked_domains

    def _load_blocked_domains(self) -> set[str]:
        if not self.blocked_file.exists():
            return set()

        data = json.loads(self.blocked_file.read_text(encoding="utf-8"))
        raw_domains = data.get("bloqueados", data.get("blocked_domains", []))
        return {normalize_domain(domain) for domain in raw_domains}


def normalize_domain(domain: str) -> str:
    clean = (domain or "").strip().lower()
    if ":" in clean:
        clean = clean.split(":", 1)[0]
    if clean.startswith("www."):
        clean = clean[4:]
    return clean
