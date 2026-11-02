import uuid
from datetime import datetime, timezone
import os
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent.parent


class RunLog:
    def __init__(self):
        self.run_id = uuid.uuid4().hex
        folder = ROOT / "logs"
        folder.mkdir(exist_ok=True)
        self.path = folder / f"{self.run_id}.jsonl"
        self.model = os.environ.get("MODEL", "")

    def write(self, event, *, ok=True, tool=None, args=None, duration_ms=0, **extra):
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            "tool": tool,
            "args": args,
            "ok": ok,
            "model": self.model,
            "duration_ms": duration_ms,
            **extra,
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")