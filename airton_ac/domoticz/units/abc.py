from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

import DomoticzEx

from airton_ac import Values


@dataclass
class Unit(ABC):
    device_name: str
    id: int
    name: str
    image: int
    unit: DomoticzEx.Unit

    TYPE: ClassVar[str]

    def __post_init__(self):
        if not self.unit:
            self._create()

    def _create(self) -> None:
        """Create the Domoticz unit"""
        name = f"{self.device_name} {self.name}"
        options = self._options
        DomoticzEx.Log(f"creating {name} unit")
        self.unit = DomoticzEx.Unit(
            Name=name,
            DeviceID=self.device_name,
            Unit=self.id,
            Image=self.image,
            TypeName=self.TYPE,
            **({"Options": options} if options else {}),
        )
        self.unit.Create()

    def _options(self) -> Optional[Dict[str, str]]:
        return None

    @abstractmethod
    def on_command(self, command: str, level: float) -> Optional[Values]:
        """Update the underlying device and return new values."""

    def update(self, value: Any) -> None:
        self._update(value)
        self.unit.Update(Log=True)

    @abstractmethod
    def _update(self, value: Any) -> None:
        """Update the Dommoticz unit values."""
