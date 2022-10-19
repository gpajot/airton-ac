from dataclasses import dataclass, field
from enum import Enum

from tinytuya import Device


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Indices(StrEnum):
    POWER = "1"
    SET_POINT = "2"
    TEMP = "3"
    MODE = "4"
    FAN = "5"
    LOW_HEAT = "8"


class Mode(StrEnum):
    COOL = "cold"
    HEAT = "heat"
    DRY = "wet"
    VENT = "fan"


class FanSpeed(StrEnum):
    QUIET = "mute"
    LOW = "low"
    AUTO = "auto"
    MEDIUM = "mid"
    HIGH = "high"


@dataclass
class Values:
    power: bool
    mode: Mode
    fan_speed: FanSpeed
    set_point: int
    temp: float
    low_heat: bool


@dataclass
class Device:
    """Interact with the Wifi device over LAN.
    Note: not using tinytuya.Contrib.ClimateDevice as values differ.
    """

    id: str
    address: str
    local_key: str
    _device: Device = field(init=False)

    def __post_init__(self):
        self._device = Device(
            dev_id=self.id,
            address=self.address,
            local_key=self.local_key,
            version=3.3,
        )

    def values(self) -> Values:
        """Get current values from the AC."""
        values = self._device.status()["dps"]
        return Values(
            power=bool(values[Indices.POWER]),
            mode=Mode(values[Indices.MODE]),
            fan_speed=FanSpeed(values[Indices.FAN]),
            set_point=int(values[Indices.SET_POINT] / 10),
            temp=values[Indices.TEMP] / 10,
            low_heat=bool(values[Indices.LOW_HEAT]),
        )

    def set_power(self, status: bool) -> Values:
        """Turn on or off."""
        values = self.values()
        if values.power is not status:
            self._device.set_status(status, Indices.POWER)
            values.power = status
        return values

    def set_mode(self, mode: Mode) -> Values:
        """Set operating mode."""
        values = self.values()
        if values.mode is not mode:
            self._device.set_value(Indices.MODE, str(mode))
            values.mode = mode
        return values

    def set_fan_speed(self, speed: FanSpeed) -> Values:
        """Set fan speed."""
        values = self.values()
        if values.fan_speed is not speed:
            self._device.set_value(Indices.FAN, str(speed))
            values.fan_speed = speed
        return values

    def set_temperature(self, temp: float) -> Values:
        """Set temperature.
        Will round and multiply by 10 so that 18.5 will be 180.
        """
        values = self.values()
        set_point = max(min(int(temp), 31), 16) * 10
        if values.set_point != set_point:
            self._device.set_value(Indices.SET_POINT, set_point)
            values.set_point = set_point
        return values
