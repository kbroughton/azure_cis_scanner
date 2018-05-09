import os
import yaml

cis_scanner_root = '~/praetorian-tools/azure_cis_scanner/'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

print(cis_structure['section_ordering'])