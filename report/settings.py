import os
import yaml
import functools

cis_scanner_root = '/praetorian-tools/azure_cis_scanner/'
scans_base = os.path.expanduser('/engagements/cis_test/scans')

@functools.lru_cache(1, typed=False)
def get_dirs(directory):
    return [x for x in os.listdir(directory) if os.path.isdir(directory)]

# figure out better way to get base dir or let user select in UI
active_subscription_dir = get_dirs(scans_base)[0]

#active_subscription_dir = "510f92e0-xxxx-yyyy-zzzz-095d37e6a299"

accounts = {}
with open(os.path.join(scans_base, 'accounts.json'), 'r') as f:
    accounts = yaml.load(f)

scans_root = os.path.join(scans_base, active_subscription_dir)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

