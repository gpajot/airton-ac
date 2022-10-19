from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Optional

import DomoticzEx

import airton_ac.device as lan


class Unit(IntEnum):
    """Unit IDs."""

    POWER = 1
    MODE = 2
    FAN = 3
    SET_POINT = 4
    TEMP = 5


class Mode(IntEnum):
    OFF = 0
    COOL = 10
    HEAT = 20
    DRY = 30
    VENT = 40

    def to_lan(self) -> lan.Mode:
        return lan.Mode[self.name]

    @classmethod
    def from_lan(cls, mode: lan.Mode) -> "Mode":
        return cls[mode.name]


class FanSpeed(IntEnum):
    OFF = 0
    QUIET = 10
    LOW = 20
    AUTO = 30
    MEDIUM = 40
    HIGH = 50

    def to_lan(self) -> lan.FanSpeed:
        return lan.FanSpeed[self.name]

    @classmethod
    def from_lan(cls, speed: lan.FanSpeed) -> "FanSpeed":
        return cls[speed.name]


@dataclass
class Device:
    name: str
    lan_device: lan.Device
    units: Dict[int, DomoticzEx.Unit]

    def __post_init__(self):
        # Create units if needed.
        if Unit.POWER not in self.units:
            name = f"{self.name} Power"
            DomoticzEx.Log(f"creating {name} unit")
            DomoticzEx.Unit(
                Name=name,
                DeviceID=self.name,
                Unit=Unit.POWER,
                Image=9,
                TypeName="Switch",
            ).Create()
        if Unit.MODE not in self.units:
            name = f"{self.name} Mode"
            DomoticzEx.Log(f"creating {name} unit")
            DomoticzEx.Unit(
                Name=name,
                device_id=self.name,
                Unit=Unit.MODE,
                Image=19,
                _type="Selector Switch",
                Options={
                    "LevelActions": "||||",
                    "LevelNames": "Off|Cool|Heat|Dry|Vent",
                    "LevelOffHidden": "true",
                    "SelectorStyle": "0",
                },
            ).Create()
        if Unit.FAN not in self.units:
            name = f"{self.name} Fan"
            DomoticzEx.Log(f"creating {name} unit")
            DomoticzEx.Unit(
                Name=name,
                device_id=self.name,
                Unit=Unit.FAN,
                Image=7,
                TypeName="Selector Switch",
                Options={
                    "LevelActions": "|||||",
                    "LevelNames": "Off|Quiet|Low|Auto|Medium|High",
                    "LevelOffHidden": "true",
                    "SelectorStyle": "0",
                },
            ).Create()
        if Unit.SET_POINT not in self.units:
            name = f"{self.name} Set point"
            DomoticzEx.Log(f"creating {name} unit")
            DomoticzEx.Unit(
                Name=name,
                device_id=self.name,
                Unit=Unit.SET_POINT,
                Image=15,
                TypeName="Set Point",
            ).Create()
        if Unit.TEMP not in self.units:
            name = f"{self.name} Temperature"
            DomoticzEx.Log(f"creating {name} unit")
            DomoticzEx.Unit(
                Name=name,
                device_id=self.name,
                Unit=Unit.TEMP,
                Image=15,
                TypeName="Temperature",
            ).Create()

    def refresh(self) -> None:
        self._refresh(self.lan_device.values())

    def _refresh(self, values: lan.Values) -> None:
        power_unit = self.units[Unit.POWER]
        if values.power and not power_unit.nValue:
            power_unit.nValue = 1
            power_unit.sValue = "On"
            power_unit.Update(Log=True)
        elif not values.power and power_unit.nValue:
            power_unit.nValue = 0
            power_unit.sValue = "Off"
            power_unit.Update(Log=True)
        mode_unit = self.units[Unit.MODE]
        new_mode = Mode.from_lan(values.mode)
        if new_mode != mode_unit.nValue:
            mode_unit.nValue = 0 if new_mode is Mode.OFF else 1
            mode_unit.sValue = str(new_mode.value)
            mode_unit.Update(Log=True)
        fan_unit = self.units[Unit.FAN]
        new_speed = FanSpeed.from_lan(values.fan_speed)
        if new_speed != fan_unit.nValue:
            fan_unit.nValue = 0 if new_speed is FanSpeed.OFF else 1
            fan_unit.sValue = str(new_speed.value)
            fan_unit.Update(Log=True)
        set_point_unit = self.units[Unit.SET_POINT]
        if (
            not set_point_unit.sValue
            or int(float(set_point_unit.sValue)) != values.set_point
        ):
            set_point_unit.sValue = str(values.set_point)
            set_point_unit.Update(Log=True)
        temp_unit = self.units[Unit.TEMP]
        if not temp_unit.sValue or float(temp_unit.sValue) != values.temp:
            temp_unit.sValue = str(values.temp)
            temp_unit.Update(Log=True)

    def on_command(self, unit_id: int, command: str, level: float) -> None:
        new_values: Optional[lan.Values] = None
        if unit_id == Unit.POWER:
            new_values = self.lan_device.set_power(command.lower() == "on")
        elif unit_id == Unit.MODE and level:
            new_values = self.lan_device.set_mode(Mode(level).to_lan())
        elif unit_id == Unit.FAN and level:
            new_values = self.lan_device.set_fan_speed(FanSpeed(level).to_lan())
        elif unit_id == Unit.SET_POINT:
            new_values = self.lan_device.set_temperature(level)

        if new_values:
            self._refresh(new_values)
