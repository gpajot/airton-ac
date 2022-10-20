from dataclasses import dataclass
from typing import Callable, ClassVar

from airton_ac import Values
from airton_ac.domoticz.units.abc import Unit


@dataclass
class SetPointUnit(Unit):
    command_func: Callable[[float], Values]

    TYPE: ClassVar[str] = "Set Point"

    def on_command(self, command: str, level: float) -> Values:
        return self.command_func(level)

    def _update(self, value: int) -> bool:
        if not self.unit.sValue or int(float(self.unit.sValue)) != value:
            self.unit.sValue = str(value)
            return True
        return False
