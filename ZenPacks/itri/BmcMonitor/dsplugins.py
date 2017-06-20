"""Monitors BMC conditions"""

import logging
log = logging.getLogger('zen.BmcMonitor')

from twisted.internet.defer import inlineCallbacks, returnValue

from Products.ZenEvents import ZenEventClasses

from Products.DataCollector.plugins.DataMaps import ObjectMap
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
     PythonDataSourcePlugin,
     )

import subprocess

class BmcPowerStatus(PythonDataSourcePlugin):
    """BMC power status data source plugin."""
    
    proxy_attributes = (
        'zBmcAddress',
        'zIpmiUsername',
        'zIpmiPassword',
    )
 
    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            context.id,
            'bmcmonitor-powerstatus',
            )

    @classmethod
    def params(cls, datasource, context):
        return {
            'zBmcAddress': context.zBmcAddress,
            'zIpmiUsername': context.zIpmiUsername,
            'zIpmiPassword': context.zIpmiPassword,
            }
    
    @inlineCallbacks
    def collect(self, config):
        log.debug("Collect for BMC Power Status ({0})".format(config.id))

        ds0 = config.datasources[0]
        results = {}

        # Collect using ipmitool
        power_status = False
        cmd_result = ''
        try:
            cmd = 'ipmitool -H {0} -I lanplus -U {1} -P {2} power status'.format(ds0.zBmcAddress, ds0.zIpmiUsername, ds0.zIpmiPassword)
            cmd_result = yield subprocess.check_output(cmd, shell=True).rstrip()
            log.info('Power Status for Device {0}: {1}'.format(ds0.zBmcAddress, cmd_result))
        except:
            log.error('Error when running ipmitool when collecting Power Status on BMC Address {0}'.format(ds0.zBmcAddress))

        if cmd_result == 'Chassis Power is on':
            power_status = True

        results['power_status'] = power_status

        returnValue(results)

    def onSuccess(self, result, config):
        data = self.new_data()

        power_status = result['power_status']

        data['maps'].append(
            ObjectMap({
                'modname': 'ZenPacks.itri.BmcMonitor.BmcServer',
                'power_status': power_status,
                }))
                
        if power_status:
            data['events'].append({
                'device': config.id,
                'summary': '{0} BMC power status is now UP'.format(config.id),
                'severity': ZenEventClasses.Clear,
                'eventClassKey': 'bmcPowerStatus',
                })
        else:
            data['events'].append({
                'device': config.id,
                'summary': '{0} BMC power status is DOWN!'.format(config.id),
                'severity': ZenEventClasses.Critical,
                'eventClassKey': 'bmcPowerStatus',
                })
        
        data['events'].append({
            'device': config.id,
            'summary': 'BMC Power Status Collector: successful collection',
            'severity': ZenEventClasses.Clear,
            'eventKey': 'bmcPowerStatusCollectionError',
            'eventClassKey': 'bmcMonitorFailure',
            })

        return data
        
    def onError(self, result, config):
        errmsg = 'BMC Power Status Collector: Error trying to collect.'
        log.error('{0}: {1}'.format(config.id, errmsg))
        
        data = self.new_data()

        data['events'].append({
            'device': config.id,
            'summary': errmsg,
            'severity': ZenEventClasses.Critical,
            'eventKey': 'bmcPowerStatusCollectionError',
            'eventClassKey': 'bmcMonitorFailure',
            })

        return data
