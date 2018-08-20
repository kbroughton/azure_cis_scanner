import os
import yaml
import functools

# set paths depending on if we are in the container or not
if os.path.exists('/praetorian-tools/azure_cis_scanner/'):
    cis_scanner_root = '/praetorian-tools/azure_cis_scanner/'
elif os.path.exists(os.path.expanduser('~/praetorian-tools/azure_cis_scanner/')):
    cis_scanner_root = os.path.expanduser('~/praetorian-tools/azure_cis_scanner/')
else:
    cis_scanner_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

print("cis_scanner_root", cis_scanner_root)

if os.path.exists(os.path.expanduser('~/engagements/cis_test/scans')):
    scans_base = os.path.expanduser('~/engagements/cis_test/scans')
elif os.path.exists('/engagements/cis_test/scans'):
    scans_base = '/engagements/cis_test/scans'
else:
    scans_base = os.path.join(cis_scanner_root, 'scans')

@functools.lru_cache(1, typed=False)
def get_dirs(directory):
    return list(reversed(sorted([x for x in os.listdir(directory) if os.path.isdir(directory) and not x.endswith('.DS_Store')])))


accounts = {}
with open(os.path.join(scans_base, 'accounts.json'), 'r') as f:
    accounts = yaml.load(f)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

