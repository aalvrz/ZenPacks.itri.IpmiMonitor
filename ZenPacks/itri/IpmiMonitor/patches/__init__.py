import logging
from importlib import import_module

log = logging.getLogger('zen.IpmiMonitor')


def optional_import(module_name, patch_module_name):
    try:
        import_module(module_name)
    except ImportError:
        pass
    else:
        try:
            import_module(
                '.{0}'.format(patch_module_name),
                'ZenPacks.itri.IpmiMonitor.patches')
        except ImportError:
            log.exception('failed to apply %s patches', patch_module_name)


optional_import('ZenPacks.itri.ServerMonitor', 'ServerMonitor')
