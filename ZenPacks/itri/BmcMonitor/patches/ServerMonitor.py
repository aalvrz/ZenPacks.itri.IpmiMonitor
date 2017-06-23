import logging
log = logging.getLogger('zen.BmcMonitor')

from Products.ZenUtils.Utils import monkeypatch
from ZenPacks.itri.ServerMonitor.ItriServer import ItriServer


# Add power_status property
ItriServer.power_status = False
ItriServer._properties += (
    {'id': 'power_status', 'type': 'boolean', 'mode': 'w'},
    )
