from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Callable, ClassVar, Dict, Generic, Type, TypeVar

from airton_ac import Values
from airton_ac.domoticz.units.abc import Unit

T = TypeVar("T", bound=Enum)


class Options(IntEnum, Generic[T]):
    AC_ENUM: ClassVar[Type[T]]

    def to_lan(self) -> T:
        return self.AC_ENUM[self.name]

    @classmethod
    def from_lan(cls, value: T) -> "Options":
        return cls[value.name]


@dataclass
class SelectorSwitchUnit(Unit, Generic[T]):
    values: Type[Options[T]]
    command_func: Callable[[T], Values]

    TYPE: ClassVar[str] = "Selector Switch"

    def on_command(self, command: str, level: float) -> Values:
        return self.command_func(self.values(level).to_lan())

    def _options(self) -> Dict[str, str]:
        labels = [f"{e.name[0]}{e.name[1:].lower()}" for e in self.values]
        return {
            "LevelActions": "|".join(["" for _ in labels]),
            "LevelNames": "|".join(labels),
            "LevelOffHidden": "true",
            "SelectorStyle": "0",
        }

    def _update(self, value: Any) -> None:
        value = self.values.from_lan(value)
        if str(value.value) != self.unit.sValue:
            self.unit.nValue = 1 if value else 0
            self.unit.sValue = str(value.value)
