import os
import yaml
import functools

cis_scanner_root = '~/praetorian-tools/azure_cis_scanner/'
scans_root = os.path.expanduser('~/owl_projects/texas_capital_bank_2018-04-1301/phases/azure/scans')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(APP_ROOT, 'static')

with open(os.path.expanduser(APP_ROOT + '/cis_structure.yaml'), 'r') as f:
    cis_structure = yaml.load(f)

import os
import json
scans_root = os.path.expanduser('~/owl_projects/texas_capital_bank_2018-04-1301/phases/azure/scans')

@functools.lru_cache(1, typed=False)
def get_dirs():
    return [x for x in os.listdir(scans_root) if os.path.isdir(scans_root)]

@functools.lru_cache(maxsize=32, typed=False)
def get_filtered_data_path(date=None):
    """
    Get the filtered data root for the scan run on date=date or latest if date=None
    Returns path, date where date is the most recent date with data <= requested date
    
    Directory structure is
    <scans_root>/scans/<date>/<section_lowercase_underscores>.json
    """
    if date:
        if os.path.exists:
            return os.path.join(scans_root, 'scans', date, 'filtered'), date
        else:
            raise ValueError("Filtered data requested for {} but file does not exist at {}".format(
                date, os.path.join(scans_root, 'scans')))
    else:
        dir_list = get_dirs(scans_root, 'scans')
        if len(dir_list) == 0:
            print("No data found in {}.  Please run scanner first".format(scans_root))
        else:
            date = sorted(dir_list)[0]
            return os.path.join(scans_root, 'scans', date, 'filtered'), date

@functools.lru_cache(maxsize=32, typed=False)
def get_filtered_data(date=None):
    """
    Returns a dict of filtered data for a specific date or latest (default)
    
    If a section is missing it will not be returned.
    The structure is {"Identity and Access Management": {"finding1": results_dict1}, "finding2": results_dict2}
    where results_dict has keys stats, metadata, items, date - where date is actual date where data was found
    """
    filtered_data_root, date = get_filtered_data_path(date)
    filtered_data = {}
    for item in cis_structure['section_ordering']:
        item = '_'.join(map(str.lower, item.split(' '))) + '_filtered.json'
        with open(item, 'r') as f:
            data = json.load(f)
            print(data)
            data['date'] = date
        filtered_data[item] = data
    return filtered_data

@functools.lru_cache(maxsize=128, typed=False)
def get_filtered_data_by_name(section_name, date=None):
    """
    Get the latest data for a section returning first found <= date
    @params sectoin_name: Name of CIS section as a string e.g. ("Identity and Access Management")
    @params date: date in format 'YYYY-M-D', i.e. strftime("%Y-%m-%d")
    @returns filtered data, date
    """
    dir_list = sorted(get_dirs())
    section_name_file = '_'.join(map(str.lower, section_name.split(' '))) + '_filtered.json'
    for dir_date in dir_list:
        if date and (dir_date > date):
            continue
        filtered_data_path = os.path.join(scans_root, dir_date, 'filtered', section_name_file)
        print(filtered_data_path)
        if os.path.exists(filtered_data_path):
            with open(filtered_data_path, 'r') as f:
                data = json.load(f)
                data['date'] = dir_date
                return data
    else:
        return None


@functools.lru_cache(maxsize=1, typed=False)
def get_latest_filtered_data(date=None):
    """
    Returns a dict as in get_filtered_data, but if a section is missing, it will search
    back in time for a date where the section does exist.
    """
    data = get_filtered_data(date)
    if not data:
        return None
    else:
        for section_name in cis_structure['section_ordering']:
            #section_name = '_'.join(map(lower, section_name.split(' '))) + '.json'
            if section_name not in data:
                section_data = get_filtered_data_by_name(section_name, date)
                if section_data:
                    data[section_name] = section_data
    return data

@functools.lru_cache(maxsize=1, typed=False)
def get_stats():
    stats = {}
    dir_list = sorted(get_dirs())
    for section_name in cis_structure['section_ordering']:
        stats[section_name] = {}
        section_name_file = '_'.join(map(str.lower, section_name.split(' '))) + '_filtered.json'
        for dir_date in dir_list:
            filtered_data_path = os.path.join(scans_root, dir_date, 'filtered', section_name_file)
            print(filtered_data_path)
            if os.path.exists(filtered_data_path):
                with open(filtered_data_path, 'r') as f:
                    data = json.load(f)
                for finding_name, finding_data in data.items():
                    if not finding_name in stats[section_name]:
                        stats[section_name][finding_name] = {}
                    stats[section_name][finding_name][dir_date] = finding_data['stats']
    print(stats)
    return stats

@functools.lru_cache(maxsize=1, typed=False)
def get_latest_stats():
    latest_stats = {}
    stats = get_stats()
    for section_name in stats:
        latest_stats[section_name] = {}
        for finding_name in stats[section_name]:
            date = max(stats[section_name][finding_name])
            latest_stats[section_name][finding_name] = {"date": date, **stats[section_name][finding_name][date]}

    return latest_stats

@functools.lru_cache(maxsize=32, typed=False)
def plot_finding(stats_df, section_name, subsection_name):

	if (not stats_df.get(section_name)) or (not stats_df.get(section_name).get(subsection_name)):
		return None

	finding_df = stats_df.loc[section_name].loc[subsection_name]
	y = finding_df["Flagged"].tolist()
	y = np.array(y)
	x = finding_df.index
	start_month = x[0].day
    
	x = np.array([str(xx.month) + '-' + ( str(xx.day) if len(str(xx.day))==2 else '0' + str(xx.day) ) for xx in x])
	print(x)
	#x = x.day
	mask = np.isfinite(y)

	fig, ax = plt.subplots()
	ax.axes.set_ylabel('Items Flagged for Finding')
	ax.axes.set_xlabel('Date')
	#ax.axes.xaxis_date()
	xlabels = ax.axes.get_xticklabels()
	#ax.axes.set_xticklabels(labels=xlabels)
	ax.set_title(subsection_name, verticalalignment='bottom')
	#ax.axes.xaxis_date()
	#ax.transAxes.transform_angles()
	line, = ax.plot(x[mask],y[mask], ls="--",lw=1)
	ax.plot(x,y, color=line.get_color(), lw=1.5)

	plt.show()


# def get_summary_stats(section=None):
# 	"""
# 	Return the sum over impacted_items in all findings in a section

# 	If section == None, sum over sections
# 	"""
# 	stats = get_stats()
# 	if section:

# 	else:
# 		for section in stats:



