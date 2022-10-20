from dataclasses import dataclass
from typing import ClassVar

from airton_ac.domoticz.units.abc import Unit


@dataclass
class TemperatureUnit(Unit):
    TYPE: ClassVar[str] = "Temperature"

    def on_command(self, command: str, level: float) -> None:
        return None

    def _update(self, value: float) -> bool:
        if not self.unit.sValue or float(self.unit.sValue) != value:
            self.unit.sValue = str(value)
            return True
        return False
