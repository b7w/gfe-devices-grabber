from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List


@dataclass
class State:
    is_locked: bool = False
    is_alive: bool = True

    is_program_opened: bool = False
    is_devices_tab_table_opened: bool = False

    records_count: int = 0

    save_as: Path = None
    save_status: str = ''

    listeners: List[Callable] = field(default_factory=list)

    def notify(self):
        for listener in self.listeners:
            listener()


class Events:
    RETURN_KEY = '<Return>'
    STATE_CHANGED = '<<StateChanged>>'


def split_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]
