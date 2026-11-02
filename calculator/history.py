"""In-memory record of past calculations."""

from collections import deque
from dataclasses import dataclass

MAX_ENTRIES = 100


@dataclass(frozen=True)
class HistoryEntry:
    expression: str
    result: str


class History:
    def __init__(self, max_entries=MAX_ENTRIES):
        self._entries = deque(maxlen=max_entries)

    def add(self, expression, result):
        entry = HistoryEntry(expression, result)
        self._entries.appendleft(entry)
        return entry

    def clear(self):
        self._entries.clear()

    def __iter__(self):
        """Iterate from the newest entry to the oldest."""
        return iter(self._entries)

    def __len__(self):
        return len(self._entries)
