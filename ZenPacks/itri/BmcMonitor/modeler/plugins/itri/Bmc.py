"""Collects BMC information"""

from twisted.internet.defer import inlineCallbacks, returnValue
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from ZenPacks.itri.BmcMonitor.lib.ipmitool import get_power_status


class Bmc(PythonPlugin):
    """Modeler plugin for BMC servers."""

    relname = 'bmcServer'
    modname = 'ZenPacks.itri.ServerMonitor.ItriServer'

    deviceProperties = PythonPlugin.deviceProperties + (
        'zBmcAddress',
        'zIpmiUsername',
        'zIpmiPassword',
        )

    @inlineCallbacks
    def collect(self, device, log):
        log.info('{0}: collecting data for device {1}'.format(
            self.name(), device.id))

        bmc_address = getattr(device, 'zBmcAddress', None)
        ipmi_username = getattr(device, 'zIpmiUsername', None)
        ipmi_password = getattr(device, 'zIpmiPassword', None)

        try:
            power_status = yield get_power_status(
                bmc_address, ipmi_username, ipmi_password)

            log.info('Power Status for device {0}: {1}'.format(
                bmc_address, power_status))
        except Exception as e:
            log.error('{0}: {1}'.format(bmc_address, e))
            returnValue(None)

        returnValue(self.objectMap({
            'power_status': power_status,
            }))

    def process(self, device, results, log):
        return results
