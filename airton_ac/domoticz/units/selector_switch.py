from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable, ClassVar, Dict, Type

from airton_ac import Values
from airton_ac.domoticz.units.abc import Unit


class Options(IntEnum):
    @property
    def ac(self) -> Type[Enum]:
        return Enum

    def to_lan(self) -> Enum:
        return self.ac[self.name]

    @classmethod
    def from_lan(cls, value: Enum) -> "Options":
        return cls[value.name]


@dataclass
class SelectorSwitchUnit(Unit):
    values: Type[Options]
    command_func: Callable[[Enum], Values]

    TYPE: ClassVar[str] = "Selector Switch"

    def on_command(self, command: str, level: float) -> Values:
        return self.command_func(self.values(int(level)).to_lan())

    def _options(self) -> Dict[str, str]:
        labels = [f"{e.name[0]}{e.name[1:].lower()}" for e in self.values]
        return {
            "LevelActions": "|".join(["" for _ in labels]),
            "LevelNames": "|".join(labels),
            "LevelOffHidden": "true",
            "SelectorStyle": "0",
        }

    def _update(self, value: Enum) -> bool:
        value = self.values.from_lan(value)
        if str(value.value) != self.unit.sValue:
            self.unit.nValue = 1 if value else 0
            self.unit.sValue = str(value.value)
            return True
        return False
