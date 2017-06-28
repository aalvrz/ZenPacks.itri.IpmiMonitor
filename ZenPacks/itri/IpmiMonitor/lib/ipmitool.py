import subprocess

def get_power_status(ip_address, username='admin', password='admin'):
    cmd = ('ipmitool -H {0} -I lanplus -U {1} -P {2} '
        'power status'.format(ip_address, username, password))

    try:
        r = subprocess.check_output(cmd, shell=True).rstrip()
    except subprocess.CalledProcessError as e:
        raise IpmitoolError('Error running command', e)

    return r == 'Chassis Power is on'

def get_power_supply(ip_address, username='admin', password='admin'):
    cmd = ('ipmitool -H {0} -I lanplus -U {1} -P {2} '
        'sdr type "Power Supply"'.format(ip_address, username, password))

    try:
        r = subprocess.check_output(cmd, shell=True).rstrip()
    except subprocess.CalledProcessError as e:
        raise IpmitoolError('Error running command', e)

    return parse_ipmi(r)

def parse_ipmi(output):
    """Parse ipmitool output into a dictionary"""
    
    result = {}

    for row in output.split('\n'):
        if '|' in row:
            dp = row.split('|')[0].lower().replace(' ', '')
            val = row.split('|')[-1].split()[0].rstrip()

            try:
                val = float(val)
            except ValueError:
                # For outputs like power supply status
                pass
                
            result[dp] = val

    return result