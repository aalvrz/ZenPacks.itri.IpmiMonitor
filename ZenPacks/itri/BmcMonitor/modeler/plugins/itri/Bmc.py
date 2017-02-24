"""Collects BMC information"""

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

import subprocess
import re

class Bmc(PythonPlugin):
    """Modeler plugin for BMC servers."""

    modname = 'ZenPacks.itri.BmcMonitor.BmcServer'
    
    deviceProperties = PythonPlugin.deviceProperties + (
        'zBmcAddress',
        'zIpmiUsername',
        'zIpmiPassword',
        )
        
    @inlineCallbacks
    def collect(self, device, log):
        log.info('Modeler {0} collecting data for device {1}'.format(self.name(), device.id))        

        bmc_address = getattr(device, 'zBmcAddress', None)
        ipmi_username = getattr(device, 'zIpmiUsername', None)
        ipmi_password = getattr(device, 'zIpmiPassword', None)

        cmd_result = ''        
        try:
            cmd = 'ipmitool -H {0} -I lanplus -U {1} -P {2} power status'.format(bmc_address, ipmi_username, ipmi_password)
            cmd_result = yield subprocess.check_output(cmd, shell=True).rstrip()
            log.info('Power Status for Device {0}: {1}'.format(bmc_address, cmd_result))
        except:
            log.error('Error when running ipmitool when collecting Power Status on BMC Address {0}'.format(bmc_address))

        # Parse the result
        power_status = False       
        if cmd_result == 'Chassis Power is on':
            power_status = True
        
        returnValue(self.objectMap({
            'power_status': power_status,
        }))
        
    def process(self, device, results, log):
        return results
