import subprocess


def get_power_status(ip_address, username='admin', password='admin'):
    cmd = ('ipmitool -H {0} -I lanplus -U {1} -P {2} '
        'power status'.format(ip_address, username, password))

    try:
        r = subprocess.check_output(cmd, shell=True).rstrip()
    except subprocess.CalledProcessError as e:
        raise

    if r == 'Chassis Power is on':
        return True

    return False
