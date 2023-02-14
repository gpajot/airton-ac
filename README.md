# airton-ac

[![tests](https://github.com/gpajot/airton-ac/workflows/Test/badge.svg?branch=main&event=push)](https://github.com/gpajot/airton-ac/actions?query=workflow%3ATest+branch%3Amain+event%3Apush)
[![version](https://img.shields.io/pypi/v/airton-ac?label=stable)](https://pypi.org/project/airton-ac/)
[![python](https://img.shields.io/pypi/pyversions/airton-ac)](https://pypi.org/project/airton-ac/)

Control an Airton AC device over LAN.
This requires having the [wifi module](https://eu.airton.shop/en/products/kit-module-wifi-pour-climatiseurs-airton-en-wifi-ready).

## Features
- asynchronous methods and transport
- persistent communication to the device
- automatic remote device state updates (remotes can still be used)
- configurable buffering for subsequent updates
- constraints between device commands
- Domoticz plugin using a dedicated thread

## Usage
See [local tuya requirements](https://github.com/gpajot/local-tuya#requirements) first to find device information.

Example usage:
```python
from local_tuya import DeviceConfig, ProtocolConfig
from airton_ac import ACDevice, ACFanSpeed


async with ACDevice(DeviceConfig(ProtocolConfig("{id}", "{address}", b"{key}"))) as device:
    await device.switch(True)
    await device.set_speed(ACFanSpeed.L2)
    await device.switch(False)
```

## Domoticz plugin
The plugin requires having fetched device information using instructions above.
Make sure to read [plugin instructions](https://www.domoticz.com/wiki/Using_Python_plugins) first.
> 💡 The Domoticz version should be `2022.1` or higher.

```shell
python -m pip install --upgrade airton-ac
python -m airton_ac.domoticz.install
```
Domoticz path defaults to `~/domoticz` but you can pass a `-p` option to the second command to change that:
```shell
python -m airton_ac.domoticz.install -p /some/other/path
```

Restart Domoticz and create a new Hardware using `Tuya Airton AC`. Fill in device information and add.
The hardware will create up to 5 devices to control the fan (all prefixed with hardware name):
- `power`: to turn on or off
- `set point`: to set the target temperature
- `temperature`: to record curent temperature as measured by the unit
- `mode`: to control operating mode
- `fan`: to control fan speed
- `eco`: toggle low heat when heating and eco-mode when cooling
- `light`: toggle display on the unit
- `swing`: toggle swing mode
- `sleep`: toggle sleep mode
- `health`: toggle health mode

You can customize the devices you want added in the hardware page.

All device names and levels can be changed once added as only IDs are used internally.

