from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from local_tuya import (
    Constraint,
    Constraints,
    DataPoint,
    Device,
    DeviceConfig,
    State,
    Values,
)


class ACDataPoint(DataPoint):
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


class ACMode(str, Enum):
    AUTO = "auto"
    COOL = "cold"
    HEAT = "heat"
    DRY = "wet"
    VENT = "fan"


class ACFanSpeed(str, Enum):
    AUTO = "auto"
    QUIET = "mute"
    L1 = "low"
    L2 = "low_mid"
    L3 = "mid"
    L4 = "mid_high"
    L5 = "high"
    TURBO = "turbo"


@dataclass
class ACState(State):
    power: bool
    set_point: float
    temp: float
    mode: ACMode
    fan_speed: ACFanSpeed
    eco: bool
    light: bool
    swing: bool
    sleep: bool
    health: bool

    @classmethod
    def load(cls, values: Values) -> "ACState":
        return cls(
            power=bool(values[ACDataPoint.POWER]),
            set_point=int(values[ACDataPoint.SET_POINT]) / 10,
            temp=int(values[ACDataPoint.TEMP]) / 10,
            mode=ACMode(values[ACDataPoint.MODE]),
            fan_speed=ACFanSpeed(values[ACDataPoint.FAN]),
            eco=bool(values[ACDataPoint.ECO]),
            light=bool(values[ACDataPoint.LIGHT]),
            swing=values[ACDataPoint.SWING] == "un_down"
            and values[ACDataPoint.SWING_DIRECTION] == ACDataPoint.SWING,
            sleep=bool(values[ACDataPoint.SLEEP]),
            health=bool(values[ACDataPoint.HEALTH]),
        )


class ACDevice(Device[ACState]):
    def __init__(
        self,
        config: DeviceConfig,
        state_updated_callback: Optional[Callable[[ACState], Any]] = None,
    ):
        super().__init__(
            config,
            ACState.load,
            state_updated_callback,
            Constraints(
                Constraint(
                    ACDataPoint.SET_POINT,
                    (ACDataPoint.MODE, {ACMode.AUTO, ACMode.VENT}),
                    (ACDataPoint.ECO, {True}),
                ),
                Constraint(
                    ACDataPoint.FAN,
                    (ACDataPoint.MODE, {ACMode.DRY}),
                ),
                Constraint(
                    ACDataPoint.FAN,
                    (ACDataPoint.MODE, {ACMode.AUTO, ACMode.DRY}),
                    (ACDataPoint.ECO, {True}),
                    restrict_to={ACFanSpeed.TURBO},
                ),
                Constraint(
                    ACDataPoint.ECO,
                    (ACDataPoint.MODE, {ACMode.AUTO, ACMode.DRY, ACMode.VENT}),
                ),
                Constraint(
                    ACDataPoint.SLEEP,
                    (ACDataPoint.MODE, {ACMode.AUTO, ACMode.VENT}),
                    (ACDataPoint.ECO, {True}),
                ),
            ),
        )

    async def switch(self, status: bool) -> None:
        """Turn on or off."""
        await self._update({ACDataPoint.POWER: status})

    async def set_point(self, temp: float) -> None:
        """Set temperature.
        Will round and multiply by 10 so that 18.5 will be 180.
        """
        set_point = max(min(round(temp), 31), 16) * 10
        await self._update({ACDataPoint.SET_POINT: set_point})

    async def set_mode(self, mode: ACMode) -> None:
        """Set operating mode."""
        await self._update({ACDataPoint.MODE: mode.value})

    async def set_fan_speed(self, speed: ACFanSpeed) -> None:
        """Set fan speed."""
        await self._update({ACDataPoint.FAN: speed.value})

    async def switch_eco(self, status: bool) -> None:
        """Toggle low heat."""
        await self._update({ACDataPoint.ECO: status})

    async def switch_light(self, status: bool) -> None:
        """Toggle light."""
        await self._update({ACDataPoint.LIGHT: status})

    async def switch_swing(self, status: bool) -> None:
        """Toggle swing."""
        await self._update(
            {
                ACDataPoint.SWING: "un_down" if status else "off",
                ACDataPoint.SWING_DIRECTION: ACDataPoint.SWING.value
                if status
                else "off",
            }
        )

    async def switch_sleep(self, status: bool) -> None:
        """Toggle sleep."""
        await self._update({ACDataPoint.SLEEP: status})

    async def switch_health(self, status: bool) -> None:
        """Toggle health."""
        await self._update({ACDataPoint.HEALTH: status})
