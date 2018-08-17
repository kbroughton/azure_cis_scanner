import functools
import yaml
from settings import *
import re


@functools.lru_cache(maxsize=32, typed=False)
def get_filtered_data_path(scans_root, date=None):
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
            date = dir_list[0]
            return os.path.join(scans_root, 'scans', date, 'filtered'), date

@functools.lru_cache(maxsize=32, typed=False)
def get_filtered_data(scans_root, date=None):
    """
    Returns a dict of filtered data for a specific date or latest (default)
    
    If a section is missing it will not be returned.
    The structure is {"Identity and Access Management": {"finding1": results_dict1}, "finding2": results_dict2}
    where results_dict has keys stats, metadata, items, date - where date is actual date where data was found
    """
    filtered_data_root, date = get_filtered_data_path(scans_root, date)
    filtered_data = {}
    for item in cis_structure['section_ordering']:
        item = '_'.join(map(str.lower, item.split(' '))) + '_filtered.json'
        with open(item, 'r') as f:
            data = yaml.load(f)
            data['date'] = date
        filtered_data[item] = data
    return filtered_data

@functools.lru_cache(maxsize=128, typed=False)
def get_filtered_data_by_name(scans_root, section_name, date=None):
    """
    Get the latest data for a section returning first found <= date
    @params sectoin_name: Name of CIS section as a string e.g. ("Identity and Access Management")
    @params date: date in format 'YYYY-M-D', i.e. strftime("%Y-%m-%d")
    @returns filtered data, date
    """
    # get date folders, most to least recent
    dir_list = get_dirs(scans_root)
    section_name_file = '_'.join(map(str.lower, section_name.split(' '))) + '_filtered.json'
    for dir_date in dir_list:
        if date and (dir_date > date):
            continue
        filtered_data_path = os.path.join(scans_root, dir_date, 'filtered', section_name_file)
        if os.path.exists(filtered_data_path):
            print('get_filtered_data_by_name', filtered_data_path)
            with open(filtered_data_path, 'r') as f:
                data = yaml.load(f)
                data['date'] = dir_date
                return data
    else:
        return None


@functools.lru_cache(maxsize=1, typed=False)
def get_latest_filtered_data(scans_root, date=None):
    """
    Returns a dict as in get_filtered_data, but if a section is missing, it will search
    back in time for a date where the section does exist.
    """
    data = get_filtered_data(scans_root, date)
    if not data:
        return None
    else:
        for section_name in cis_structure['section_ordering']:
            #section_name = '_'.join(map(lower, section_name.split(' '))) + '.json'
            if section_name not in data:
                section_data = get_filtered_data_by_name(scans_root, section_name, date)
                if section_data:
                    data[section_name] = section_data
    return data

@functools.lru_cache(maxsize=1, typed=False)
def get_stats(scans_root):
    stats = {}
    dir_list = get_dirs(scans_root)
    print("get_stats dir_list {}".format(dir_list))
    for section_name in cis_structure['section_ordering']:
        stats[section_name] = {}
        section_name_file = '_'.join(map(str.lower, section_name.split(' '))) + '_filtered.json'
        for dir_date in dir_list:
            filtered_data_path = os.path.join(scans_root, dir_date, 'filtered', section_name_file)
            if os.path.exists(filtered_data_path):
                with open(filtered_data_path, 'r') as f:
                    data = yaml.load(f)
                for finding_name, finding_data in data.items():
                    if not finding_name in stats[section_name]:
                        stats[section_name][finding_name] = {}
                    stats[section_name][finding_name][dir_date] = finding_data['stats']
    return stats

@functools.lru_cache(maxsize=1, typed=False)
def get_latest_stats(scans_root):
    latest_stats = {}
    stats = get_stats(scans_root)
    for section_name in stats:
        latest_stats[section_name] = {}
        for finding_name in stats[section_name]:
            print("HHHHHH {}".format(stats[section_name][finding_name]))
            date = max(stats[section_name][finding_name])
            latest_stats[section_name][finding_name] = {"date": date, **stats[section_name][finding_name][date]}

    return latest_stats

def get_finding_name(finding_name, subsection_name):
    """
    Get finding name from CIS_TOC using over-ride (finding_name) but defaulting to parsed subsection_name
    """
    if finding_name:
        return finding_name
    else:
        return underscore_name(subsection_name)

def underscore_name(subsection_name):
    return '_'.join(map(lambda x: x.lower(), subsection_name.split(' ')))

def title_except(string):
    articles = ['a', 'an', 'of', 'the', 'is', 'not', 'for', 'if']
    word_list = re.split(' ', string)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in articles else word.capitalize())
    return " ".join(final)

def get_finding_index(findings_list, finding):
    for finding_entry in findings_list:
        if finding_entry['subsection_name'] == finding:
            return finding_entry
    raise ValueError("finding {} not found in {}".format(finding, findings_list))


# def get_summary_stats(section=None):
# 	"""
# 	Return the sum over impacted_items in all findings in a section

# 	If section == None, sum over sections
# 	"""
# 	stats = get_stats()
# 	if section:

# 	else:
# 		for section in stats:



