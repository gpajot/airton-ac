from dataclasses import dataclass
from typing import Callable, ClassVar

from airton_ac import Values
from airton_ac.domoticz.units.abc import Unit


@dataclass
class SwitchUnit(Unit):
    command_func: Callable[[bool], Values]

    TYPE: ClassVar[str] = "Switch"

    def on_command(self, command: str, level: float) -> Values:
        return self.command_func(command.lower() == "on")

    def _update(self, value: bool) -> bool:
        if value and not self.unit.nValue:
            self.unit.nValue = 1
            self.unit.sValue = "On"
            return True
        if not value and self.unit.nValue:
            self.unit.nValue = 0
            self.unit.sValue = "Off"
            return True
        return False
