# ZenPacks.itri.BmcMonitor

Monitor BMC status of servers.

## Configuration

A valid BMC IP address must be added to the devices that wished to be monitored. 
Additionally, valid ipmitool username and password credentials must be 
configured as well. All these configurations are handled through the following 
zProperties:

|       Name      |   Type   | Default | Category |    Description    |
|:---------------:|:--------:|:-------:|:--------:|:-----------------:|
| `zBmcAddress`   |  Boolean | False   | BMC      | BMC IP Address    |
| `zIpmiUsername` |  String  | `admin` | IPMI     | ipmitool username |
| `zIpmiPassword` | Password | `admin` | IPMI     | ipmitool password |

## Usage

After the ZenPack is installed, configure the `zBmcAddress` property for a 
specific device in the `/Server/Linux` or `/Server/SSH/Linux/NovaHost` device 
class.

The `BMC` monitoring template's data source plugin will then use this address to 
begin querying the BMC machine for the power status using ipmitool. The default 
cycle time is 30 seconds.

A power status indicator similar to the ping status indicator will be displayed 
in the device's page:

![Power Status Indicator](screenshots/power_status.jpg)

## Dependencies

The following ZenPacks are required:

- [ZenPacks.zenoss.ZenPackLib
v2](https://www.zenoss.com/product/zenpacks/zenpacklib)
- [ZenPacks.zenoss.PythonCollector](https://www.zenoss.com/product/zenpacks/pythoncollector)
- ZenPacks.itri.ServerMonitor v2+
