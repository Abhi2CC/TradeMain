from collections import defaultdict
import json
from pathlib import Path

class LevelManager:
    def __init__(self, levels_file: Path) -> None:
        self.levels_file = levels_file
        self.levels = []
        self._indexed = defaultdict(list)

    def load(self) -> None:
        data = json.loads(self.levels_file.read_text(encoding='utf-8'))
        self.levels = data.get('levels', [])
        self._indexed.clear()
        for level in self.levels:
            level.setdefault('status', 'ACTIVE')
            self._indexed[(level['index'], level['timeframe'])].append(level)

    def reload(self) -> None:
        self.load()

    def active_levels(self, index: str, timeframe: str) -> list[dict]:
        return [l for l in self._indexed.get((index, timeframe), []) if l.get('status') == 'ACTIVE']

    def mark_used(self, level: dict) -> None:
        level['status'] = 'USED'
