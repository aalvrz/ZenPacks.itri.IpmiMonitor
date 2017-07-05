import logging
log = logging.getLogger('zen.IpmiMonitor')

from twisted.internet.defer import inlineCallbacks, returnValue

from Products.ZenEvents import ZenEventClasses
from Products.DataCollector.plugins.DataMaps import ObjectMap
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
     PythonDataSourcePlugin,
     )

from ZenPacks.itri.IpmiMonitor.lib import ipmitool


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
            'ipmimonitor-powerstatus',
            )

    @classmethod
    def params(cls, datasource, context):
        return {
            'zBmcAddress': context.zBmcAddress,
            'zIpmiUsername': context.zIpmiUsername,
            'zIpmiPassword': context.zIpmiPassword,
            'deviceClass': context.getDeviceClassName(),
            }

    @inlineCallbacks
    def collect(self, config):
        log.info("Collecting BMC Power Status for {0}".format(config.id))

        data = self.new_data()
        ds0 = config.datasources[0]

        # Use zBmcAddress property if the device is not in /Server/BMC
        # device class. Otherwise use device's own IP address.
        if "BMC" in ds0.params['deviceClass']:
            ip = config.id
        else:
            ip = ds0.zBmcAddress

        # Collect using ipmitool
        try:
            power_status = yield ipmitool.get_power_status(
                ip, ds0.zIpmiUsername, ds0.zIpmiPassword)

            log.info('Power Status for Device {0}: {1}'.format(
                ds0.zBmcAddress, power_status))
        except Exception as e:
            log.error('{0}: {1}'.format(ds0.zBmcAddress, e))
            returnValue(None)

        data['maps'].append(
            ObjectMap({
                'modname': 'ZenPacks.itri.ServerMonitor.ItriServer',
                'powerStatus': power_status,
                }))

        if power_status:
            summary = '{0} BMC power status is now UP'.format(config.id)
            severity = ZenEventClasses.Clear
        else:
            summary = '{0} BMC power status is DOWN!'.format(config.id)
            severity = ZenEventClasses.Critical

        data['events'].append({
            'device': config.id,
            'summary': summary,
            'severity': severity,
            'eventClassKey': 'bmcPowerStatus',
            })

        returnValue(data)

    def onSuccess(self, result, config):
        result['events'].append({
            'device': config.id,
            'summary': 'BMC Power Status Collector: successful collection',
            'severity': ZenEventClasses.Clear,
            'eventKey': 'bmcPowerStatusCollectionError',
            'eventClassKey': 'bmcMonitorFailure',
            })

        return result

    def onError(self, result, config):
        errmsg = 'Error trying to collect BMC power status.'
        log.error('{0}: {1}'.format(config.id, errmsg))

        data = self.new_data()

        data['maps'].append(
            ObjectMap({
                'modname': 'ZenPacks.itri.ServerMonitor.ItriServer',
                'powerStatus': False,
                }))

        data['events'].append({
            'device': config.id,
            'summary': errmsg,
            'severity': ZenEventClasses.Critical,
            'eventKey': 'bmcPowerStatusCollectionError',
            'eventClassKey': 'bmcMonitorFailure',
            })

        return data


class PowerSupplyDataSourcePlugin(PythonDataSourcePlugin):
    """Collect power supply status using ipmitool"""

    proxy_attributes = (
        'zIpmiUsername',
        'zIpmiPassword',
    )

    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            context.id,
            'ipmimonitor-powersupply',
            )

    @classmethod
    def params(cls, datasource, context):
        return {}

    @inlineCallbacks
    def collect(self, config):
        log.info('Collecting for IPMI power supply data source {0}'.format(
            config.id))

        data = self.new_data()
        ds0 = config.datasources[0]

        try:
            power_supply = yield ipmitool.get_power_supply(
                config.id, ds0.zIpmiUsername, ds0.zIpmiPassword)
        except Exception as e:
            log.error('{0}: {1}'.format(config.id, e))
            returnValue(None)

        for dp, val in power_supply.iteritems():
            dpname = '_'.join((ds0.datasource, dp))

            log.debug('{0}: {1}'.format(dpname, val))
            data['values'][None][dpname] = (int('Presence' == val), 'N')

        returnValue(data)
        