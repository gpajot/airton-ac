from typing import Dict, Optional


class DomoticzEx:
    @classmethod
    def Log(cls, s: str) -> None:
        ...

    @classmethod
    def Heartbeat(cls, i: int) -> None:
        ...

    class Unit:
        def __init__(
            self,
            Name: str,
            DeviceID: str,
            Unit: int,
            TypeName: str,
            Image: Optional[int] = 0,
            Options: Optional[Dict[str, str]] = None,
        ):
            self.nValue: float = 0
            self.sValue: str = ""

        def Create(self) -> None:
            ...

        def Update(self, Log: bool) -> None:
            ...


class Device:
    Units: Dict[int, DomoticzEx.Unit] = {}


Parameters: Dict[str, str] = {}
Devices: Dict[str, Device] = {}
