import json
import threading
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LOG_FILE = ROOT_DIR / "storage" / "access_log.jsonl"


class AccessAudit:
    def __init__(self, log_file: Path = DEFAULT_LOG_FILE):
        self.log_file = Path(log_file)
        self._lock = threading.Lock()

    def record(self, url: str, domain: str, action: str, status_code: int, filtered_terms_count: int) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "domain": domain,
            "action": action,
            "status_code": status_code,
            "filtered_terms_count": filtered_terms_count,
        }

        with self._lock:
            with self.log_file.open("a", encoding="utf-8") as file:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")
