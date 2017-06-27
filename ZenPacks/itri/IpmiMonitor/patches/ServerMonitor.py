import logging
log = logging.getLogger('zen.IpmiMonitor')

from Products.Zuul.infos import ProxyProperty

from ZenPacks.itri.ServerMonitor.ItriServer import ItriServer, ItriServerInfo


# Add power_status property
ItriServer.powerStatus = False
ItriServer._properties += (
    {'id': 'powerStatus', 'type': 'boolean', 'mode': 'w'},
    )

# Make the property available through the API
ItriServerInfo.powerStatus = ProxyProperty('powerStatus')
