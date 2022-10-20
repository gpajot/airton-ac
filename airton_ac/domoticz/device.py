from enum import IntEnum
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from airton_ac.domoticz.types import DomoticzEx
else:
    import DomoticzEx

import airton_ac.device as lan
from airton_ac.domoticz.units import (
    Options,
    SelectorSwitchUnit,
    SetPointUnit,
    SwitchUnit,
    TemperatureUnit,
    Unit,
)


class UnitId(IntEnum):
    """Unit IDs."""

    POWER = 1
    SET_POINT = 2
    TEMP = 3
    MODE = 4
    FAN = 5
    ECO = 6
    LIGHT = 7
    SWING = 8
    SLEEP = 9
    HEALTH = 10


class Mode(Options):
    OFF = 0
    AUTO = 10
    COOL = 20
    HEAT = 30
    DRY = 40
    VENT = 50

    @property
    def ac(self) -> Type[lan.Mode]:
        return lan.Mode


class FanSpeed(Options):
    OFF = 0
    AUTO = 10
    QUIET = 20
    L1 = 30
    L2 = 40
    L3 = 50
    L4 = 60
    L5 = 70
    TURBO = 80

    @property
    def ac(self) -> Type[lan.FanSpeed]:
        return lan.FanSpeed


class Device:
    def __init__(
        self, name: str, lan_device: lan.Device, units: Dict[int, DomoticzEx.Unit]
    ):
        self.lan_device = lan_device
        self.units: Dict[int, Unit] = {
            UnitId.POWER: SwitchUnit(
                device_name=name,
                id=UnitId.POWER,
                image=9,
                name="power",
                _unit=units.get(UnitId.POWER),
                command_func=lan_device.set_power,
            ),
            UnitId.SET_POINT: SetPointUnit(
                device_name=name,
                id=UnitId.SET_POINT,
                name="set point",
                image=0,
                _unit=units.get(UnitId.SET_POINT),
                command_func=lan_device.set_temperature,
            ),
            UnitId.TEMP: TemperatureUnit(
                device_name=name,
                id=UnitId.TEMP,
                name="temperature",
                image=0,
                _unit=units.get(UnitId.TEMP),
            ),
            UnitId.MODE: SelectorSwitchUnit(
                device_name=name,
                id=UnitId.MODE,
                image=19,
                name="mode",
                _unit=units.get(UnitId.MODE),
                values=Mode,
                command_func=lan_device.set_mode,  # type: ignore
            ),
            UnitId.FAN: SelectorSwitchUnit(
                device_name=name,
                id=UnitId.FAN,
                image=7,
                name="fan",
                _unit=units.get(UnitId.FAN),
                values=FanSpeed,
                command_func=lan_device.set_fan_speed,  # type: ignore
            ),
            UnitId.ECO: SwitchUnit(
                device_name=name,
                id=UnitId.ECO,
                image=15,
                name="eco",
                _unit=units.get(UnitId.ECO),
                command_func=lan_device.set_eco,
            ),
            UnitId.LIGHT: SwitchUnit(
                device_name=name,
                id=UnitId.LIGHT,
                image=0,
                name="light",
                _unit=units.get(UnitId.LIGHT),
                command_func=lan_device.set_light,
            ),
            UnitId.SWING: SwitchUnit(
                device_name=name,
                id=UnitId.SWING,
                image=7,
                name="swing",
                _unit=units.get(UnitId.SWING),
                command_func=lan_device.set_swing,
            ),
            UnitId.SLEEP: SwitchUnit(
                device_name=name,
                id=UnitId.SLEEP,
                image=9,
                name="sleep",
                _unit=units.get(UnitId.SLEEP),
                command_func=lan_device.set_sleep,
            ),
            UnitId.HEALTH: SwitchUnit(
                device_name=name,
                id=UnitId.HEALTH,
                image=11,
                name="health",
                _unit=units.get(UnitId.HEALTH),
                command_func=lan_device.set_health,
            ),
        }

    def refresh(self) -> None:
        self._update(self.lan_device.values())

    def _update(self, values: lan.Values) -> None:
        self.units[UnitId.POWER].update(values.power)
        self.units[UnitId.SET_POINT].update(values.set_point)
        self.units[UnitId.TEMP].update(values.temp)
        self.units[UnitId.MODE].update(values.mode)
        self.units[UnitId.FAN].update(values.fan_speed)
        self.units[UnitId.ECO].update(values.eco)
        self.units[UnitId.LIGHT].update(values.light)
        self.units[UnitId.SWING].update(values.swing)
        self.units[UnitId.SLEEP].update(values.sleep)
        self.units[UnitId.HEALTH].update(values.health)

    def on_command(self, unit_id: int, command: str, level: float) -> None:
        values = self.units[unit_id].on_command(command, level)
        if values:
            self._update(values)
