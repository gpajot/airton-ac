from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set, Tuple, Union

import tinytuya


class Command(str, Enum):
    POWER = "1"
    SET_POINT = "2"
    TEMP = "3"
    MODE = "4"
    FAN = "5"
    ECO = "8"
    LIGHT = "13"
    SWING = "15"
    SWING_DIRECTION = "107"
    SLEEP = "109"
    HEALTH = "110"


class Mode(str, Enum):
    AUTO = "auto"
    COOL = "cold"
    HEAT = "heat"
    DRY = "wet"
    VENT = "fan"


class FanSpeed(str, Enum):
    AUTO = "auto"
    QUIET = "mute"
    L1 = "low"
    L2 = "low_mid"
    L3 = "mid"
    L4 = "mid_high"
    L5 = "high"
    TURBO = "turbo"


RawValue = Union[bool, int, str]
RawValues = Dict[str, RawValue]


@dataclass
class Values:
    power: bool
    set_point: int
    temp: float
    mode: Mode
    fan_speed: FanSpeed
    eco: bool
    light: bool
    swing: bool
    sleep: bool
    health: bool


@dataclass
class Exclusion:
    command: Command
    values: Set[RawValue]

    def applicable(self, values: RawValues) -> bool:
        return values[self.command.value] in values


@dataclass
class Constraint:
    command: Command
    values: Optional[Set[RawValue]]
    exclusions: Tuple[Exclusion, ...]

    def ok(self, command: str, value: RawValue, values: RawValues) -> bool:
        if command != self.command or self.values and value not in self.values:
            # Constraint is not applicable.
            return True
        for exclusion in self.exclusions:
            if exclusion.applicable(values):
                return False
        return True


CONSTRAINTS: Tuple[Constraint, ...] = (
    Constraint(
        Command.SET_POINT,
        None,
        (
            Exclusion(Command.MODE, {Mode.AUTO.value, Mode.VENT.value}),
            Exclusion(Command.ECO, {True}),
        ),
    ),
    Constraint(Command.FAN, None, (Exclusion(Command.MODE, {Mode.DRY.value}),)),
    Constraint(
        Command.FAN,
        {FanSpeed.TURBO.value},
        (
            Exclusion(Command.MODE, {Mode.AUTO.value, Mode.DRY.value}),
            Exclusion(Command.ECO, {True}),
        ),
    ),
    Constraint(
        Command.ECO,
        None,
        (Exclusion(Command.MODE, {Mode.AUTO.value, Mode.DRY.value, Mode.VENT.value}),),
    ),
    Constraint(
        Command.SLEEP,
        None,
        (
            Exclusion(Command.MODE, {Mode.AUTO.value, Mode.VENT.value}),
            Exclusion(Command.ECO, {True}),
        ),
    ),
)


class Device:
    """Interact with the Wifi device over LAN.
    Note: not using tinytuya.Contrib.ClimateDevice as values differ.
    """

    def __init__(self, _id: str, address: str, local_key: str):
        self._device = tinytuya.Device(
            dev_id=_id,
            address=address,
            local_key=local_key,
            version=3.3,
        )

    def _raw_values(self) -> RawValues:
        return self._device.status()["dps"]

    def values(self, values: Optional[RawValues] = None) -> Values:
        """Get current values from the AC."""
        values = values or self._raw_values()
        return Values(
            power=bool(values[Command.POWER.value]),
            set_point=int(int(values[Command.SET_POINT.value]) / 10),
            temp=int(values[Command.TEMP.value]) / 10,
            mode=Mode(values[Command.MODE.value]),
            fan_speed=FanSpeed(values[Command.FAN.value]),
            eco=bool(values[Command.ECO.value]),
            light=bool(values[Command.LIGHT.value]),
            swing=values[Command.SWING.value] == "un_down"
            and values[Command.SWING_DIRECTION.value] == Command.SWING.value,
            sleep=bool(values[Command.SLEEP.value]),
            health=bool(values[Command.HEALTH.value]),
        )

    def _update(self, values: RawValues) -> Values:
        current = self._raw_values()
        updated: RawValues = {}
        for k, v in values.items():
            if v != current[k]:
                # Check constraints.
                for constraint in CONSTRAINTS:
                    if not constraint.ok(k, v, current):
                        continue
                updated[k] = v
        if updated:
            payload = self._device.generate_payload(tinytuya.CONTROL, values)
            self._device._send_receive(payload)
            return self.values()
        return self.values(current)

    def set_power(self, status: bool) -> Values:
        """Turn on or off."""
        return self._update({Command.POWER.value: status})

    def set_temperature(self, temp: float) -> Values:
        """Set temperature.
        Will round and multiply by 10 so that 18.5 will be 180.
        """
        set_point = max(min(round(temp), 31), 16) * 10
        return self._update({Command.SET_POINT.value: set_point})

    def set_mode(self, mode: Mode) -> Values:
        """Set operating mode."""
        return self._update({Command.MODE.value: mode.value})

    def set_fan_speed(self, speed: FanSpeed) -> Values:
        """Set fan speed."""
        return self._update({Command.FAN.value: speed.value})

    def set_eco(self, status: bool) -> Values:
        """Toggle low heat."""
        return self._update({Command.ECO.value: status})

    def set_light(self, status: bool) -> Values:
        """Toggle light."""
        return self._update({Command.LIGHT.value: status})

    def set_swing(self, status: bool) -> Values:
        """Toggle swing."""
        return self._update(
            {
                Command.SWING.value: "un_down" if status else "off",
                Command.SWING_DIRECTION.value: Command.SWING.value if status else "off",
            }
        )

    def set_sleep(self, status: bool) -> Values:
        """Toggle sleep."""
        return self._update({Command.SLEEP.value: status})

    def set_health(self, status: bool) -> Values:
        """Toggle health."""
        return self._update({Command.HEALTH.value: status})
