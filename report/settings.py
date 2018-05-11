import os
import yaml

cis_scanner_root = '~/praetorian-tools/azure_cis_scanner/'

def get_filtered_data_root(date=None):
	"""
	Get the filtered data root for the scan run on date=date or latest if date=None

	Directory structure is
	<cis_scanner_root>/scans/<date>/<section_lowercase_underscores>.json
	"""
	if date:
		if os.path.exists:
			return os.path.join(cis_scanner_root, 'scans', date)
		else:
			raise ValueError("Filtered data requested for {} but file does not exist at {}".format(date, os.path.join(cis_scanner_root, 'scans')))
	else:
		filtered_data_root = sort(os.path.dirlist(os.path.join(cis_scanner_root, 'scans')))[0]
		return filtered_data_root

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

