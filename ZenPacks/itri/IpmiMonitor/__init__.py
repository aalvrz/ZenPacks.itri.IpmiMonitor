from ZenPacks.zenoss.ZenPackLib import zenpacklib
CFG = zenpacklib.load_yaml()

import logging
log = logging.getLogger('zen.IpmiMonitor')

schema = CFG.zenpack_module.schema

BMC_PLUGINS = ['itri.Bmc']

BMC_TEMPLATES = ['BMC']

class ZenPack(schema.ZenPack):

    def install(self, app):
        self._update_plugins('/Server/SSH/Linux/NovaHost')
        self._update_templates('/Server/SSH/Linux/NovaHost')

        super(ZenPack, self).install(app)

    def _update_plugins(self, organizer):
        try:
            dc = self.dmd.Devices.getOrganizer(organizer)
        except Exception as e:
            log.error(e)
        else:
            dc.setZenProperty( 
                'zCollectorPlugins', dc.zCollectorPlugins + BMC_PLUGINS)

    def _update_templates(self, organizer):
        try:
            dc = self.dmd.Devices.getOrganizer(organizer)
        except Exception as e:
            log.error(e)
        else:
            dc.setZenProperty(
                'zDeviceTemplates', dc.zDeviceTemplates + BMC_TEMPLATES)

# Patch last to avoid import recursion problems
from . import patches
