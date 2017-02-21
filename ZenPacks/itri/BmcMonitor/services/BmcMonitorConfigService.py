import logging
log = logging.getLogger('zen.bmcmond')

import Globals
from Products.ZenUtils.Utils import unused
from Products.ZenCollector.services.config import CollectorConfigService

unused(Globals)

class BmcMonitorConfigService(CollectorConfigService):
    """
    ZenHub service for the bmcmond collector daemon.
    """

    def _filterDevice(self, device):
        # First use standard filtering.
        filter = CollectorConfigService._filterDevice(self, device)

        # If the standard filtering logic said the device shouldn't be filtered
        # we can setup some other contraint.        
        has_flag = False
        if filter:
           # Return only devices that are in the /Server/ Device Class
           try:
              if '/Server/' in device.getDeviceClassName():
                 has_flag = True
           except Exception as e:
              print e

        return CollectorConfigService._filterDevice(self, device) and has_flag

    def _createDeviceProxy(self, device):
        proxy = CollectorConfigService._createDeviceProxy(self, device)
        
        proxy.configCycleInterval = 5 * 60 #5 minutes
        proxy.datapoints = []

        perfServer = device.getPerformanceServer()

        return proxy


if __name__ == '__main__':
    from Products.ZenHub.ServiceTester import ServiceTester
    tester = ServiceTester(BmcMonitorConfigService)
    def printer(config):
        # Fill this out
        print config.datapoints
        
    tester.printDeviceProxy = printer
    tester.showDeviceInfo()
