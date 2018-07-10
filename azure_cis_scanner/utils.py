
import datetime
import os
import subprocess
import sys
import re
import functools
import json
import requests
import traceback


token_expiry = None
access_token = None
filtered_data_dir = ''
scan_data_dir = ''
raw_data_dir = ''


def set_data_paths(subscription_dirname, base_dir='.'):
    """
    Given a base_dir, create subdirs scans/{day}/raw
                                          /filtered
    @returns: scan_data_dir, raw_data_dir
    """
    # Get day in YYYY-MM-DD format

    day = datetime.datetime.now().strftime('%Y-%m-%d')

    if base_dir.startswith('/'):
        base_dir = os.path.abspath(base_dir)
    elif base_dir.startswith('~'):
        base_dir = os.path.expanduser(base_dir)
    scan_data_dir = os.path.join(base_dir, 'scans', subscription_dirname, day)
    print("scan_data_dir", scan_data_dir)
    raw_data_dir = scan_data_dir + '/raw'
    print("raw_data_dir", raw_data_dir)
    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)
    filtered_data_dir = scan_data_dir + '/filtered'
    print("filtered_data_dir", filtered_data_dir)
    if not os.path.exists(filtered_data_dir):
        os.makedirs(filtered_data_dir)
    return scan_data_dir, raw_data_dir, filtered_data_dir   


def call(command, retrieving_access_token=False):
    #if not valid_token() and not retrieving_access_token:
    #    get_access_token()
    if(isinstance(command, str)) :
        command = command.split()           # subprocess needs an array of arguments
    try :
        print('running: ', command)
        result = subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT).decode('utf-8')
        print("results", result)
        return result
    except Exception as e:
        print("An exception occurred while processing command " + str(command) + " Halting execution!")
        print(e)
        print(traceback.format.exc())
        sys.exit()


def verify_subscription_id_format(subscriptionId) :
    r = re.compile("([a-f]|[0-9]){8}-([a-f]|[0-9]){4}-([a-f]|[0-9]){4}-([a-f]|[0-9]){4}-([a-f]|[0-9]){12}")
    if r.match(subscriptionId):
        return True
    else :
        return False


def valid_token():
     if (not token_expiry) or (datetime.datetime.utcnow() > token_expiry):
        return False
     else:
        return True


def get_active_account():
    return jsonify(call("az account show"))


def get_subscription_id(account) :
    return account["id"]


def get_subscription_name(subscription_id, accounts):
    for account in accounts:
        if subscription_id == accounts['id']:
            return accounts['name']
    raise ValueError("subscription_id {} not found in accounts {}".format(subscription_id, accounts))


def get_access_token():
    global token_expiry, access_token
    if not valid_token():
        complete_token = call("az account get-access-token", retrieving_access_token=True)
        complete_token = jsonify(complete_token)
        access_token = complete_token["accessToken"]
        token_expiry = complete_token["expiresOn"]
        print(token_expiry)
        token_expiry = datetime.datetime.strptime(token_expiry, '%Y-%m-%d %H:%M:%S.%f')
    return access_token, token_expiry


def make_request(url, args=[]):
    print('requesting ', url)
    authorization_headers = {"Authorization" : "Bearer " + get_access_token()}
    r = requests.get(url, headers=authorization_headers)
    return r.text


def jsonify(jsonString) :
    return json.loads(jsonString)


def stringify(jsonObject) :
    return json.dumps(jsonObject)