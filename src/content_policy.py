import json
from pathlib import Path
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BLOCKED_FILE = ROOT_DIR / "settings" / "blocked.json"


class ContentPolicy:
    def __init__(self, blocked_file: Path = DEFAULT_BLOCKED_FILE):
        self.blocked_file = Path(blocked_file)
        self._last_loaded_mtime: float | None = None
        self.blocked_domains = self._load_blocked_domains()

    def is_blocked(self, domain: str) -> bool:
        self._reload_if_changed()
        normalized = normalize_domain(domain)
        return normalized in self.blocked_domains

    def _reload_if_changed(self) -> None:
        current_mtime = self._get_mtime()
        if current_mtime != self._last_loaded_mtime:
            self.blocked_domains = self._load_blocked_domains()

    def _load_blocked_domains(self) -> set[str]:
        if not self.blocked_file.exists():
            self._last_loaded_mtime = None
            return set()

        data = json.loads(self.blocked_file.read_text(encoding="utf-8"))
        self._last_loaded_mtime = self._get_mtime()
        raw_domains = data.get("bloqueados", data.get("blocked_domains", []))
        return {normalize_domain(domain) for domain in raw_domains}

    def _get_mtime(self) -> float | None:
        if not self.blocked_file.exists():
            return None
        return self.blocked_file.stat().st_mtime


def normalize_domain(domain: str) -> str:
    clean = (domain or "").strip().lower()
    if "://" in clean:
        parsed = urlparse(clean)
        clean = parsed.hostname or parsed.netloc or clean
    if ":" in clean:
        clean = clean.split(":", 1)[0]
    if clean.startswith("www."):
        clean = clean[4:]
    return clean
