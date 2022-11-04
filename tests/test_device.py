import pytest

from airton_ac.device import Command, Device, FanSpeed, Mode, Values


class TestDevice:
    @pytest.fixture()
    def device(self, mocker):
        dev = Device(
            _id="id",
            address="address",
            local_key="local_key",
            set_point_offset=-1,
            temp_offset=-2,
        )
        mocker.patch.object(
            dev,
            "_raw_values",
            return_value={
                Command.POWER.value: True,
                Command.SET_POINT.value: 200,
                Command.TEMP.value: 215,
                Command.MODE.value: Mode.HEAT.value,
                Command.FAN.value: FanSpeed.L1.value,
                Command.ECO.value: False,
                Command.LIGHT.value: True,
                Command.SWING.value: "un_down",
                Command.SWING_DIRECTION.value: Command.SWING.value,
                Command.SLEEP.value: False,
                Command.HEALTH.value: True,
            },
        )
        return dev

    def test_values(self, device):
        assert device.values() == Values(
            power=True,
            set_point=19,
            temp=19.5,
            mode=Mode.HEAT,
            fan_speed=FanSpeed.L1,
            eco=False,
            light=True,
            swing=True,
            sleep=False,
            health=True,
        )

    @pytest.mark.parametrize(
        ("current", "update", "expected"),
        [
            # Nothing should do nothing.
            ({}, {}, {}),
            # Unchanged values should be ignored.
            (
                {Command.POWER.value: True, Command.HEALTH.value: False},
                {Command.POWER.value: True, Command.HEALTH.value: True},
                {Command.HEALTH.value: True},
            ),
            # Set point cannot be set on auto.
            (
                {
                    Command.MODE.value: Mode.AUTO.value,
                    Command.ECO.value: False,
                    Command.SET_POINT.value: 170,
                },
                {Command.SET_POINT.value: 160},
                {},
            ),
            # Set point cannot be set on eco.
            (
                {
                    Command.MODE.value: Mode.HEAT.value,
                    Command.ECO.value: True,
                    Command.SET_POINT.value: 170,
                },
                {Command.SET_POINT.value: 160},
                {},
            ),
            # Set point can be set for other modes.
            (
                {
                    Command.MODE.value: Mode.HEAT.value,
                    Command.ECO.value: False,
                    Command.SET_POINT.value: 170,
                },
                {Command.SET_POINT.value: 160},
                {Command.SET_POINT.value: 160},
            ),
        ],
    )
    def test__validate_payload(self, current, update, expected, device):
        assert device._validate_payload(current, update) == expected

    @pytest.mark.parametrize(
        ("temp", "expected"),
        [
            (19, 200),
            (19.4, 200),
            (19.7, 210),
        ],
    )
    def test_set_temperature(self, temp, expected, device, mocker):
        mocker.patch.object(device, "_update", side_effect=lambda d: d)
        assert device.set_temperature(temp) == {Command.SET_POINT.value: expected}

    @pytest.mark.parametrize(
        ("swing", "expected_swing", "expected_direction"),
        [
            (True, "un_down", Command.SWING.value),
            (False, "off", "off"),
        ],
    )
    def test_set_swing(self, swing, expected_swing, expected_direction, device, mocker):
        mocker.patch.object(device, "_update", side_effect=lambda d: d)
        assert device.set_swing(swing) == {
            Command.SWING.value: expected_swing,
            Command.SWING_DIRECTION.value: expected_direction,
        }
