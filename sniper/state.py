"""Simple disk-persisted position tracker to avoid duplicate trades across restarts."""

import json
import os
from pathlib import Path
from threading import Lock

STATE_FILE = Path(os.getenv("POSITIONS_FILE", "positions.json"))

class PositionTracker:
    def __init__(self):
        self._lock = Lock()
        self.positions: set[str] = set()
        self._load()

    def _load(self):
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text())
                if isinstance(data, list):
                    self.positions = set(data)
            except Exception as exc:
                print("State load error:", exc)

    def _save(self):
        try:
            STATE_FILE.write_text(json.dumps(list(self.positions)))
        except Exception as exc:
            print("State save error:", exc)

    def has(self, key: str) -> bool:
        return key in self.positions

    def add(self, key: str) -> None:
        with self._lock:
            self.positions.add(key)
            self._save()