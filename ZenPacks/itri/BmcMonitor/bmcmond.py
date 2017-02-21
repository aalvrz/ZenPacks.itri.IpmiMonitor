import logging
log = logging.getLogger('zen.bmcmond')
logging.basicConfig()

import Globals
import zope.component
import zope.interface

from twisted.internet import defer

from Products.ZenCollector.daemon import CollectorDaemon
from Products.ZenCollector.interfaces \
    import ICollectorPreferences, IScheduledTask, IEventService, IDataService

from Products.ZenCollector.tasks \
    import SimpleTaskFactory, SimpleTaskSplitter, TaskStates

from Products.ZenUtils.observable import ObservableMixin

# unused is way to keep Python linters from complaining about imports that we
# don't explicitely use. Occasionally there is a valid reason to do this.
from Products.ZenUtils.Utils import unused

# We must import our ConfigService here so zenhub will allow it to be
# serialized and deserialized. We'll declare it unused to satisfy linters.
from ZenPacks.itri.BmcMonitor.services.BmcMonitorConfigService import BmcMonitorConfigService

unused(Globals)
unused(BmcMonitorConfigService)

import subprocess
import re

from Products.ZenEvents.ZenEventClasses import Error, Critical, Clear
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit

class BmcMonitorPreferences(object):
    zope.interface.implements(ICollectorPreferences)

    def __init__(self):
        self.collectorName = 'bmcmond'
        self.configurationService = \
            "ZenPacks.itri.BmcMonitor.services.BmcMonitorConfigService"

        # How often the daemon will collect each device. Specified in seconds.
        self.cycleInterval = 1 * 60

        # How often the daemon will reload configuration. In seconds.
        self.configCycleInterval = 1* 60

        self.options = None

    def buildOptions(self, parser):
        pass

    def postStartup(self):
        pass

class BmcMonitorTask(ObservableMixin):
    zope.interface.implements(IScheduledTask)

    def __init__(self, taskName, deviceId, interval, taskConfig):
        super(BmcMonitorTask, self).__init__()
        self._taskConfig = taskConfig

        self._eventService = zope.component.queryUtility(IEventService)
        self._dataService = zope.component.queryUtility(IDataService)
        self._preferences = zope.component.queryUtility(
            ICollectorPreferences, 'bmcmond')

        # All of these properties are required to implement the IScheduledTask
        # interface.
        self.name = taskName
        self.configId = deviceId
        self.interval = interval
        self.state = TaskStates.STATE_IDLE

    def doTask(self):
        # This method must return a deferred because the collector framework
        # is asynchronous.
        log.info('BMC Monitor Daemon processing for device {0}'.format(self.configId))
        
        dmd = ZenScriptBase(connect=True, noopts=True).dmd
        device = dmd.Devices.findDevice(self.configId)
        
        power_status = self._getPowerStatus(device.zBmcAddress, device.zIpmiUsername, device.zIpmiPassword)
        
        # Send/Clear event depending on the current and obtained Power Status value
        if power_status == False:
            msg = '{0} Power Status is DOWN!'.format(self.configId)
            log.warning(msg)
            self._eventService.sendEvent(dict(summary=msg, message=msg, component=self._preferences.collectorName, eventClass='/Status/PowerStatus', 
                ipAddress=self.configId, device=self.configId, severity=Critical, agent=self._preferences.collectorName))
                
        elif power_status == None:
            msg = '{0}: Cannot get Power Status'.format(self.configId)
            log.warning(msg)
            self._eventService.sendEvent(dict(summary=msg, message=msg, component=self._preferences.collectorName, eventClass='/Status/PowerStatus',
                ipAddress=self.configId, device=self.configId, severity=Critical, agent=self._preferences.collectorName))
                                                
        elif power_status and not device.power_status:
            msg = '{0} Power Status is UP!'.format(self.configId)
            self._eventService.sendEvent(dict(summary=msg, message=msg, component=self._preferences.collectorName, eventClass='/Status/PowerStatus',
                ipAddress=self.configId, device=self.configId, severity=Clear, agent=self._preferences.collectorName))
                            
        device.power_status = power_status
        
        # Get Power Usage and write to RRD File
        power_usage = self._getPowerUsage(device.zBmcAddress, device.zIpmiUsername, device.zIpmiPassword)
        self._writeRRD(device, 'Power_Power', power_usage)

        commit()
        sync()
               
        d = defer.Deferred()
        return d

    def _getPowerStatus(self, bmc_address, ipmi_username, ipmi_password):
        power_status = False
        ipmi_output = 'Chassis Power is off'
        try:
            # Run ipmi tool POWER STATUS command for the device
            ipmi_output = subprocess.check_output('ipmitool -H {0} -I lanplus -U {1} -P {2} power status'.format(bmc_address, ipmi_username, ipmi_password), shell=True).rstrip()
            log.info('Power Status for Device {0}: {1}'.format(bmc_address, ipmi_output))
        except subprocess.CalledProcessError as e:
            log.info('Error when running ipmitool when collecting Power Status on BMC Address {0}'.format(bmc_address))
            power_status = None

        if ipmi_output == 'Chassis Power is on':
            power_status = True

        return power_status


    def _getPowerUsage(self, device_ip, ipmi_username, ipmi_password):
        power_usage = 0.00
        try:
            # Run ipmi tool to get POWER USAGE for the device
            power_usage_output = subprocess.check_output("ipmitool -I lanplus -H {0} -U {1} -P {2} sdr | grep Chassis | awk '{{print $1 $2 $3 $4}}'".format(device_ip, ipmi_username, ipmi_password), shell=True).rstrip()
            log.info('Power Usage for Device {0}: {1}'.format(device_ip, power_usage_output))
        except subprocess.CalledProcessError as e:
            log.info('Error when running ipmitool when collecting Power Usage on device {0}'.format(device_ip))
            
        regex = re.compile("ChassisPWR.|[0-9]+(\.[0-9][0-9]?)?")
        
        if regex.match(power_usage_output):
            power_usage = float(power_usage_output.split('|')[1])
            
        return power_usage

    def _writeRRD(self, device, rrd_file_name, value):
        try:
            from Products.ZenRRD.RRDUtil import RRDUtil
            
            path = 'Devices/{0}/{1}'.format(device.id, rrd_file_name)
            rrd = RRDUtil('', 300)
            
            rrd_save_val = rrd.save(path, value, "GAUGE", min=0, max=None)
            
            log.info('Wrote to {0} with value {1}'.format(rrd.performancePath(path + '.rrd'), rrd_save_val))
            
        except Exception as e:
            summary = "Unable to save data value into RRD file {0} - Exception: {1}".format(rrd.performancePath(path + '.rrd'), e.message)
            log.error(summary)
        
    # cleanup is required to implement the IScheduledTask interface.
    def cleanup(self):
        pass


if __name__ == '__main__':
    myPreferences = BmcMonitorPreferences()
    myTaskFactory = SimpleTaskFactory(BmcMonitorTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)

    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
