from typing import Dict

from local_tuya import DeviceConfig, ProtocolConfig
from local_tuya.domoticz import (
    Parameter,
    PluginMetadata,
    UnitId,
    UnitManager,
    compose,
    debounce,
    install_plugin,
    moving_average,
    selector_switch_unit,
    set_point_unit,
    switch_unit,
    temperature_unit,
)

from airton_ac.device import (
    ACDevice,
    ACFanSpeed,
    ACMode,
    ACState,
)


def _get_metadata() -> PluginMetadata:
    return PluginMetadata(
        name="Tuya Airton AC",
        package="airton_ac",
        description={
            "p": [
                {"h2": "Tuya Airton AC"},
                {
                    "h3": "Features",
                    "ul": {
                        "li": [
                            "Control a Airton AC over LAN",
                            "Automatically receive new device state (compatible with remote usage)",
                        ]
                    },
                },
                {
                    "h3": "Devices",
                    "ul": {
                        "li": [
                            "power - Turn the unit on or off",
                            "set_point - Define the target temperature",
                            "temp - Reported room temperature",
                            "mode - Set the operating mode",
                            "fan - Set fan speed",
                            "eco - Turn low heat when heating and eco-mode when cooling on or off",
                            "light - Turn the display on or off",
                            "swing - Turn the moving swing mode on or off",
                            "sleep - Turn the sleep mode on or off",
                            "health - Turn the health mode on or off",
                        ]
                    },
                },
            ]
        },
        parameters=(
            Parameter(
                field="Mode1",
                label="Debounce updates",
                description="Group updates made within n seconds.",
                required=True,
                default="0",
            ),
        ),
    )


class ACUnitId(UnitId):
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


def on_start(
    protocol_config: ProtocolConfig,
    parameters: Dict[str, str],
    manager: UnitManager[ACState],
) -> ACDevice:
    device = ACDevice(
        config=DeviceConfig(
            protocol=protocol_config,
            debounce_updates=float(parameters.get("Mode1") or 0),
        ),
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.POWER,
            name="power",
            image=9,
            command_func=device.switch,
        ),
        lambda s: s.power,
    )
    manager.register(
        set_point_unit(
            id_=ACUnitId.SET_POINT,
            name="set point",
            image=0,
            command_func=device.set_point,
        ),
        lambda s: s.set_point,
    )
    manager.register(
        temperature_unit(
            id_=ACUnitId.TEMP,
            name="temperature",
            image=0,
            # In some cases, temperature can oscillate a lot.
            value_preprocessor=compose(
                moving_average(4),
                debounce(30),
            ),
        ),
        lambda s: s.temp,
    )
    manager.register(
        selector_switch_unit(
            id_=ACUnitId.MODE,
            name="mode",
            image=19,
            enum=ACMode,
            command_func=device.set_mode,
        ),
        lambda s: s.mode,
    )
    manager.register(
        selector_switch_unit(
            id_=ACUnitId.FAN,
            name="fan",
            image=7,
            enum=ACFanSpeed,
            command_func=device.set_fan_speed,
        ),
        lambda s: s.fan_speed,
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.ECO,
            name="eco",
            image=15,
            command_func=device.switch_eco,
        ),
        lambda s: s.eco,
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.LIGHT,
            name="light",
            image=0,
            command_func=device.switch_light,
        ),
        lambda s: s.light,
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.SWING,
            name="swing",
            image=7,
            command_func=device.switch_swing,
        ),
        lambda s: s.swing,
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.SLEEP,
            name="sleep",
            image=9,
            command_func=device.switch_sleep,
        ),
        lambda s: s.sleep,
    )
    manager.register(
        switch_unit(
            id_=ACUnitId.HEALTH,
            name="health",
            image=11,
            command_func=device.switch_health,
        ),
        lambda s: s.health,
    )
    return device


if __name__ == "__main__":
    install_plugin(
        _get_metadata(),
        on_start,
        "airton_ac.domoticz.install",
        ACUnitId,
    )
