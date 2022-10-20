# airton-ac

[![tests](https://github.com/gpajot/airton-ac/workflows/Test/badge.svg?branch=main&event=push)](https://github.com/gpajot/airton-ac/actions?query=workflow%3ATest+branch%3Amain+event%3Apush)
[![version](https://img.shields.io/pypi/v/airton-ac?label=stable)](https://pypi.org/project/airton-ac/)
[![python](https://img.shields.io/pypi/pyversions/airton-ac)](https://pypi.org/project/airton-ac/)

Control an Airton AC device over the local area network without using any cloud.
This requires having the [wifi module](https://eu.airton.shop/en/products/kit-module-wifi-pour-climatiseurs-airton-en-wifi-ready).

## Usage
You can use this library to control a device programmatically with `airton_ac.Device` or through the Domoticz plugin.

### Requirements
To control a device you will need these 3 things:
- the device ID
- the device local IP address
- the device local key (encryption key generated upon pairing)

To get those, follow instructions from [TinyTuya](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).
> ⚠️ Important considerations:
> - After pairing the devices, assign static IPs in your router.
> - Data center should be `Central Europe Data Center`.

After having run the wizard, you can run `python -m tinytuya scan` to get a summary of devices.
Once you have the information you can unlink the devices from the SmartLife app and delete your accounts.

> ⚠️ Keep in mind that if you reset or re-pair devices the local key will change.

### Domoticz plugin
The plugin requires having fetched device information using instructions above.
Make sure to read [plugin instructions](https://www.domoticz.com/wiki/Using_Python_plugins) first.
The Domoticz version should be `2022.1` or higher.

```shell
python3 -m pip install airton-ac
python3 -m airton_ac.domoticz.install
```

Restart Domoticz and create a new Hardware using `AirtonAC`. You will need one per device, fill in information and add.
The hardware will create 10 devices to control the AC (all prefixed with hardware name):
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
