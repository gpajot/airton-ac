import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Heartbeat:
    interval: int
    func: Callable[[], None]
    _last: float = field(default=0, init=False)

    def __post_init__(self):
        self()

    def __call__(self) -> None:
        now = time.monotonic()
        if not self._last or now - self._last > self.interval:
            self.func()
            self._last = now
