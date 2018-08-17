# import time
# import os
# from azure_cis_scanner import utils
#
# try:
#     account = utils.get_active_account()
# except:
#     print("No Azure account associated with this session. Please authenticate to continue.")
#     utils.call("az login")
#     account = utils.get_active_account()
#     print("Pausing for 5 seconds")
#     subscription_id = account['id']
#     subscription_name = account['name']
#     print("Using current subscription_id {} {}".format(subscription_id, subscription_name))
#     print("Re-run with --subscription-id if you wish to change")
#     time.sleep(5)
# subscription_id = account['id']
# subscription_name = account['name']
# # create a part-friendly/part-uniquie-id name
# access_token, token_expiry = utils.get_access_token()
# subscription_dirname = subscription_name.split(' ')[0] + '-' + subscription_id.split('-')[0]
# scans_dir = os.path.expanduser('~/engagements')
# scan_data_dir, raw_data_dir, filtered_data_dir = utils.set_data_paths(subscription_dirname, scans_dir)