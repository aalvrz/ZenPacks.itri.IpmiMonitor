from . import zenpacklib

CFG = zenpacklib.load_yaml()

class ZenPack(schema.ZenPack):
    def install(self, app):
        try:
            server_dc = self.dmd.Devices.getOrganizer('/Server')
        except Exception:
            pass
        else:
            bmc_plugin = ['itri.Bmc']
            ps = list(server_dc.zCollectorPlugins) + bmc_plugin
            self.device_classes['/Server'].zProperties['zCollectorPlugins'] = ps

            super(ZenPack, self).install(app)

# Patch last to avoid import recursion problems
from . import patches
