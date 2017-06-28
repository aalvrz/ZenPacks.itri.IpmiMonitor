import subprocess


def get_power_status(ip_address, username='admin', password='admin'):
    cmd = ('ipmitool -H {0} -I lanplus -U {1} -P {2} '
        'power status'.format(ip_address, username, password))

    try:
        r = subprocess.check_output(cmd, shell=True).rstrip()
    except subprocess.CalledProcessError:
        raise

    if r == 'Chassis Power is on':
        return True

    return False
    
def parse_ipmi(output):
    """Parse ipmitool output into a dictionary"""
    
    result = {}

    for row in output.split('\n'):
        if '|' in row:
            dp = row.split('|')[0].lower().rstrip()
            val = float(row.split('|')[-1].split()[0].rstrip())
            result[dp] = val

    return result