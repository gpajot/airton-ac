import sys
from typing import Dict, Union

import pytest

from airton_ac.device import ACDataPoint, ACDevice, ACFanSpeed, ACMode, ACState


def test_state_load():
    values: Dict[str, Union[str, int, bool]] = {
        ACDataPoint.POWER.value: True,
        ACDataPoint.SET_POINT.value: 200,
        ACDataPoint.TEMP.value: 215,
        ACDataPoint.MODE.value: ACMode.HEAT.value,
        ACDataPoint.FAN.value: ACFanSpeed.L1.value,
        ACDataPoint.ECO.value: False,
        ACDataPoint.LIGHT.value: True,
        ACDataPoint.SWING.value: "un_down",
        ACDataPoint.SWING_DIRECTION.value: ACDataPoint.SWING.value,
        ACDataPoint.SLEEP.value: False,
        ACDataPoint.HEALTH.value: True,
    }
    assert ACState.load(values) == ACState(
        power=True,
        set_point=20,
        temp=21.5,
        mode=ACMode.HEAT,
        fan_speed=ACFanSpeed.L1,
        eco=False,
        light=True,
        swing=True,
        sleep=False,
        health=True,
    )


class TestACDevice:
    @pytest.fixture()
    def device(self, mocker):
        mocker.patch("local_tuya.Device.__init__")
        return ACDevice(mocker.Mock())

    @pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="requires python3.8 or higher for AsyncMock",
    )
    @pytest.mark.parametrize(
        ("temp", "expected"),
        [
            (19, 190),
            (19.4, 190),
            (19.7, 200),
        ],
    )
    async def test_set_point(self, temp, expected, device, mocker):
        update = mocker.patch.object(device, "_update")

        await device.set_point(temp)

        update.assert_awaited_once_with({ACDataPoint.SET_POINT: expected})

    @pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="requires python3.8 or higher for AsyncMock",
    )
    @pytest.mark.parametrize(
        ("swing", "expected_swing", "expected_direction"),
        [
            (True, "un_down", ACDataPoint.SWING),
            (False, "off", "off"),
        ],
    )
    async def test_switch_swing(
        self, swing, expected_swing, expected_direction, device, mocker
    ):
        update = mocker.patch.object(device, "_update")

        await device.switch_swing(swing)

        update.assert_awaited_once_with(
            {
                ACDataPoint.SWING: expected_swing,
                ACDataPoint.SWING_DIRECTION: expected_direction,
            }
        )
