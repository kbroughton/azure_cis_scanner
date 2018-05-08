import datetime
import os
import yaml

def set_data_paths(base_dir='.'):
    """
    Given a base_dir, create subdirs scans/{day}/raw
                                          /filtered
    @returns: scan_data_dir, raw_data_dir
    """
    # Get day in YYYY-MM-DD format

    day = datetime.datetime.today()
    day = '-'.join(map(str, day.timetuple()[0:3]))

    scan_data_dir = os.path.join(base_dir, 'scans', day)
    print("scan_data_dir", scan_data_dir)
    raw_data_dir = scan_data_dir + '/raw'
    print("raw_data_dir", raw_data_dir)
    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)
    filtered_data_dir = scan_data_dir + '/filtered'
    if not os.path.exists(filtered_data_dir):
        os.makedirs(filtered_data_dir)
    return scan_data_dir, raw_data_dir