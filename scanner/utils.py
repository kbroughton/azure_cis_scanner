import datetime
import os
import subprocess
import sys
import re
import json
import requests

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

def call(command) :
    if(isinstance(command, str)) :
        command = command.split()           # subprocess needs an array of arguments
    try :
        return subprocess.check_output(command).decode('utf-8')
    except:
        print("An exception occurred when processing command " + str(command) + " Halting execution!")
        sys.exit()

def verify_subscription_id_format(subscriptionId) :
    r = re.compile("([a-f]|[0-9]){8}-([a-f]|[0-9]){4}-([a-f]|[0-9]){4}-([a-f]|[0-9]){4}-([a-f]|[0-9]){12}")
    if r.match(subscriptionId) :
        return True
    else :
        return False

def get_subscription_id() :
    current_context = jsonify(call("az account show"))
    return current_context["id"]

def get_access_token() :
    complete_token = call("az account get-access-token")
    complete_token = jsonify(complete_token)
    access_token = complete_token["accessToken"]
    return access_token

def make_request(url, args=[]):
    authorization_headers = {"Authorization" : "Bearer " + get_access_token()}
    r = requests.get(url, headers=authorization_headers)
    return r.text

def jsonify(jsonString) :
    return json.loads(jsonString)

def stringify(jsonObject) :
    return json.dumps(jsonObject)

