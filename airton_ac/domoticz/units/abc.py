from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional

if TYPE_CHECKING:
    from airton_ac.domoticz.types import DomoticzEx
else:
    import DomoticzEx

from airton_ac import Values


@dataclass
class Unit(ABC):
    device_name: str
    id: int
    name: str
    image: int
    _unit: Optional[DomoticzEx.Unit]
    unit: DomoticzEx.Unit = field(init=False)

    TYPE: ClassVar[str]

    def __post_init__(self):
        self.unit = self._unit or self._create()

    def _create(self) -> DomoticzEx.Unit:
        """Create the Domoticz unit"""
        name = f"{self.device_name} {self.name}"
        options = self._options()
        DomoticzEx.Log(f"creating {name} unit")
        unit = DomoticzEx.Unit(
            Name=name,
            DeviceID=self.device_name,
            Unit=self.id,
            Image=self.image,
            TypeName=self.TYPE,
            **({"Options": options} if options else {}),
        )
        unit.Create()
        return unit

    def _options(self) -> Optional[Dict[str, str]]:
        return None

    @abstractmethod
    def on_command(self, command: str, level: float) -> Optional[Values]:
        """Update the underlying device and return new values."""

    def update(self, value: Any) -> None:
        if self._update(value):
            self.unit.Update(Log=True)

    @abstractmethod
    def _update(self, value: Any) -> bool:
        """Update the Dommoticz unit values."""
