# airton-ac
Control an Airton AC device over LAN.
This requires having the [wifi module](https://eu.airton.shop/en/products/kit-module-wifi-pour-climatiseurs-airton-en-wifi-ready).

## Usage
You can use this library to control a device programmatically with `airton_ac.Device` or through the Domoticz plugin.

### Requirements
To control a device you will need these 3 things:
- the device ID
- the device local IP address
- the device local key (encryption key generated upon pairing)

To get those, follow instructions from [TinyTuya](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).
> ⚠️ Data center should be `Central Europe Data Center`.

After having run the wizard, you can run `python -m tinytuya scan` to get a summary of devices.
Once you have the information you can unlink the devices from the SmartLife app and delete your accounts.

> ⚠️ Keep in mind that if you reset or re-pair devices the local key will change.

### Domoticz plugin
The plugin requires having fetched device information using instructions above.
Make sure to read [plugin instructions](https://www.domoticz.com/wiki/Using_Python_plugins) first.
The Domoticz version should be `2022.1` or higher.

```shell
python3 -m pip install airton_ac
python3 -m airton_ac.domoticz.install
```

Restart Domoticz and create a new Hardware using `AirtonAC`. You will need one per device, fill in information and add.
The hardware will create several devices to control the AC (all prefixed with hardware name):
- `Power`: to turn on or off
- `Mode`: to control operating mode
- `Fan`: to control fan speed
- `Set point`: to set the target temperature
- `Temperature`: to record curent temperature as measured by the unit
- `Low heat`: to turn on low heat
