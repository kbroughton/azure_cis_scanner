import os
import yaml
import functools

# set paths depending on if we are in the container or not

# if os.path.exists(os.path.expanduser('~/engagements/cis_test/scans')):
#     scans_base = os.path.expanduser('~/engagements/cis_test/scans')
# elif os.path.exists('/engagements/cis_test/scans'):
#     scans_base = '/engagements/cis_test/scans'
# else:
#     scans_base = os.path.join(os.getcwd(), 'scans')

#accounts = {}
# accounts_path = os.path.join(scans_base, 'accounts.json')
# with open(accounts_path, 'r') as f:
#     accounts = yaml.load(f)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f, Loader=yaml.Loader)

