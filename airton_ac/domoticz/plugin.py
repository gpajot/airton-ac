"""
<plugin key="AirtonAC" name="Airton AC" author="gab@les-cactus.co" version="1.0.0" wikilink="https://github.com/gpajot/airton-ac#domoticz-plugin" externallink="https://github.com/gpajot/airton-ac">
    <description>
        <h2>Airton AC plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Control one AC using LAN</li>
            <li>Update values from AC periodically</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Power - Turn the AC on or off</li>
            <li>Mode - Select the operating mode</li>
            <li>Fan - Select fan speed</li>
            <li>Set point - Define the current temperature set point</li>
            <li>Temperature - The room temperature</li>
        </ul>
    </description>
    <params>
        <param field="Username" label="Device ID" required="true"/>
        <param field="Address" label="Device IP Address" required="true"/>
        <param field="Password" label="Device local key"/>
        <param field="Mode1" label="Refresh interval (s)" requires="true" default="300"/>
    </params>
</plugin>
"""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from airton_ac.domoticz.types import Devices, DomoticzEx, Parameters
else:
    import DomoticzEx

import airton_ac as ac
from airton_ac.domoticz.device import Device
from airton_ac.domoticz.heartbeat import Heartbeat

device: Optional[Device] = None
heartbeat: Optional[Heartbeat] = None


def onStart():
    global device, heartbeat
    name = Parameters["Name"]
    device = Device(
        name=name,
        lan_device=ac.Device(
            _id=Parameters["Username"],
            address=Parameters["Address"],
            local_key=Parameters["Password"],
        ),
        units=Devices[name].Units if name in Devices else {},
    )
    interval = int(Parameters["Mode1"])
    DomoticzEx.Heartbeat(min(15, interval))
    heartbeat = Heartbeat(interval, device.refresh)


def onHeartbeat():
    if heartbeat:
        heartbeat()


def onCommand(_, unit_id, command, level, __):
    if device:
        device.on_command(unit_id, command, level)
