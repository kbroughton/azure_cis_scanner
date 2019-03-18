import datetime
import os
import yaml
import json

from azure_cis_scanner import utils
from azure_cis_scanner.utils import load_resource_groups

activity_logs_path = os.path.join(config['raw_data_dir'], 'activity_logs.json')
storage_accounts_path = os.path.join(config['raw_data_dir'], 'storage_accounts.json')
resource_groups_path = os.path.join(config['raw_data_dir'], 'resource_groups.json')
storage_accounts_filtered_path = os.path.join(config['filtered_data_dir'], 'storage_accounts_filtered.json')

def get_storage_accounts(storage_accounts_path):
    """
    Query Azure api for storage accounts info and save to disk
    """
    storage_accounts_cmd = "az storage account list"
    storage_accounts = json.loads(utils.call(storage_accounts_cmd))
        
    with open(storage_accounts_path, 'w') as f:
        json.dump(storage_accounts, f, indent=4, sort_keys=True)
    return storage_accounts

def load_storage_accounts(storage_accounts_path):
    with open(storage_accounts_path, 'r') as f:
        storage_accounts = yaml.load(f, Loader=yaml.Loader)
    return storage_accounts

# timedelta=90 days can cause BadRequest error depending on timezone
# https://github.com/Azure/azure-cli/issues/4885
activity_log_timedelta_days = 89
activity_logs_starttime_timedelta = datetime.timedelta(days=activity_log_timedelta_days)
def get_start_time(timedelta=activity_logs_starttime_timedelta):
    """
    Given datetime.timedelta(days=days, hours=hours), return string in iso tz format 
    """
    return datetime.datetime.strftime(datetime.datetime.now() - timedelta, "%Y-%m-%dT%H:%M:%SZ")

def get_activity_logs(activity_logs_path, resource_groups):
    if os.path.exists(activity_logs_path):
        print("activity_logs_path {} exists, using existing values".format(activity_logs_path))
        return
    activity_logs = {}
    start_time = get_start_time(activity_logs_starttime_timedelta)
    for resource_group in resource_groups:
        resource_group = resource_group['name']
        activity_log_cmd = "az monitor activity-log list --resource-group {resource_group} --start-time {start_time}".format(
            resource_group=resource_group, start_time=start_time)
        activity_log = json.loads(utils.call(activity_log_cmd))
        activity_logs[resource_group] = activity_log
    with open(activity_logs_path, 'w') as f:
        json.dump(activity_logs, f, indent=4, sort_keys=True)
    return activity_logs    

def load_activity_logs(activity_logs_path):
    with open(activity_logs_path, 'r') as f:
        activity_logs = yaml.load(f, Loader=yaml.Loader)
    return activity_logs



#################
# Tests
#################

def secure_transfer_required_is_set_to_enabled_3_1(storage_accounts):
    items_flagged_list = []
    for account in storage_accounts:
        name = account['name']
        resource_group = account['resourceGroup']
        enabled = account['enableHttpsTrafficOnly']
        if enabled != True:
            items_flagged_list.append((resource_group, name))
    stats = {'items_flagged': len(items_flagged_list), "items_checked": len(storage_accounts)}
    metadata = {"finding_name": "secure_transfer_required_is_set_to_enabled",
                "negative_name": "secure_transfer_required_not_enabled",
                "columns": ["Resource Group", "Storage Account Name"]}
    return {"items": items_flagged_list, 
            "stats": stats, 
            "metadata": metadata }
            
# default behavior now
# def storage_service_encryption_is_set_to_enabled_for_blob_service_3_2(storage_accounts):
#     items_flagged_list = []
#     for account in storage_accounts:
#         if account['encryption']['services']['blob'] and (account['encryption']['services']['blob']['enabled'] != True):
#             items_flagged_list.append((account['resourceGroup'], account['name']))

#     stats = {'items_flagged': len(items_flagged_list),
#              'items_checked': len(storage_accounts)}
#     metadata = {"finding_name": "storage_service_encryption_is_set_to_enabled_for_blob_service",
#                 "negative_name": "storage_service_encryption_not_enabled_for_blob_service",
#                 "columns": ["Resource Group","Storage Account Name"]}
    
#     return {"items": items_flagged_list, "stats": stats, "metadata": metadata }

# may need to run section 6 Networking first to get activity_log
def storage_account_access_keys_are_periodically_regenerated_3_2(activity_logs, storage_accounts, resource_groups):
    items_flagged_list = []
    
    max_rotation_days = 90
    most_recent_rotations = {}
    for resource_group in resource_groups:
        resource_group_name = resource_group['name']
        for log in activity_logs[resource_group_name]:
            if log["authorization"] and (log["authorization"]["action"] == "Microsoft.Storage/storageAccounts/regenerateKey/action"):
                scope = log["authorization"]["scope"]
                _, _, _, resource_group, _, _, _, storage_account_name = scope.split('/')
                timestamp = log["eventTimestamp"]
                event_day = timestamp.split('T')[0]
                event_day = datetime.datetime.strptime(event_time, '%Y-%m-%d')
                status = log["status"]["localizedValue"]
                if status == "Success":
                    # fromtimestamp(0) gives smallest date possible in epoch time
                    existing_update = most_recent_rotations.get(storage_account, datetime.datetime.fromtimestamp(0))
                    most_recent_rotations[storage_account] = max(existing_update, event_time)

    for storage_account in storage_accounts:
        resource_group = storage_account["resourceGroup"]
        storage_account_name = storage_account['name']
        items_flagged_list.append((resource_group, storage_account_name, str(most_recent_rotations.get(storage_account_name, "No rotation"))))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}
    metadata = {"finding_name": "storage_account_access_keys_are_periodically_regenerated",
                "negative_name": "storage_account_access_keys_not_periodically_regenerated",
                "columns": ["Resource Group", "Storage Account", "Rotation Date"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

           
def storage_account_queues_log_crud_operations_3_3(storage_accoutns):
    #az storage logging show --services q --account-name <storageAccountName>az storage logging show --services q --account-name <storageAccountName>
    pass

def shared_access_signature_tokens_expire_within_an_hour_3_4(storage_accounts):
    """
    There is no automation possible for this currently
    Manual
    """
    pass

def shared_access_signature_tokens_are_allowed_only_over_https_3_5(storage_accounts):
    """
    There is no automation possible for this currently
    Manual
    """
    pass
   
# Deprecated - default behavior                                   
# def storage_service_encryption_is_set_to_enabled_for_file_service_3_6(storage_accounts):
#     items_flagged_list = []
#     stats = {}
#     for account in storage_accounts:
#         if account['encryption']['services']['file'] and (account['encryption']['services']['file']['enabled'] != True):
#             items_flagged_list.append((account['name']))

#     stats = {'items_flagged': len(items_flagged_list),
#              'items_checked': len(storage_accounts)}
#     metadata = {"finding_name": "storage_service_encryption_is_set_to_enabled_for_file_service",
#                 "negative_name": "storage_service_encryption_not_enabled_for_file_service",
#                 "columns": ["Storage Account Name"]}

#     return {"items": items_flagged_list, "stats": stats, "metadata": metadata}


def public_access_level_is_set_to_private_for_blob_containers_3_6(storage_accounts):
    items_flagged_list = []
    items_checked = 0
    for account in storage_accounts:
        account_name = account["name"]
        resource_group = account["resourceGroup"]
        # get a key that works.  likely this will be a specific key not key[0]
        keys_cmd = "az storage account keys list --account-name {account_name} --resource-group {resource_group}".format(
            account_name=account_name, resource_group=resource_group)
        keys = json.loads(utils.call(keys_cmd))
        account_key = keys[0]['value']
        container_list_cmd = "az storage container list --account-name {account_name} --account-key {account_key}".format(
            account_name=account_name, account_key=account_key)
        container_list = json.loads(utils.call(container_list_cmd))
        for container in container_list:
            print(container)
            items_checked += 1
            public_access = container["properties"]["publicAccess"]
            if public_access == True:
                items_flagged_list.append((account_name, container))
    stats = {'items_flagged': len(items_flagged_list), "items_checked": items_checked}
    metadata = {"finding_name": "public_access_level_is_set_to_private_for_blob_containers",
                "negative_name": "public_access_level_not_private_for_blob_containers",
                "columns": ["Storage Account Name", "Container"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata }

def storage_network_default_access_rule_set_to_deny_3_7(storage_accounts):
    #az storage account list --query '[*].networkRuleSet'
    items_flagged_list = []
    for account in storage_accounts:
        account_name = account["name"]
        default_action = account["networkRuleSet"]["defaultAction"]
        if default_action == "Allow":
            items_flagged_list.append((account_name, default_action))
    stats = {'items_flagged': len(items_flagged_list), "items_checked": len(storage_accounts)}
    metadata = {"finding_name": "storage_default_network_access_rule_set_to_deny",
                "negative_name": "storage_default_network_access_rule_not_set_to_deny",
                "columns": ["Storage Account Name", "Default Action"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata }

def get_data():
    """
    Generate json for the storage_accounts findings
    """
    resource_groups = load_resource_groups(resource_groups_path)
    print(resource_groups)
    get_activity_logs(activity_logs_path, resource_groups)
    get_storage_accounts(storage_accounts_path)

def test_controls():
    """
    Generate filtered (failing) output in json
    """
    resource_groups = load_resource_groups(resource_groups_path)
    storage_accounts = load_storage_accounts(storage_accounts_path)
    activity_logs = load_activity_logs(activity_logs_path)
    
    storage_results = {}
    storage_results['secure_transfer_required_is_set_to_enabled'] = secure_transfer_required_is_set_to_enabled_3_1(storage_accounts)
    #storage_results['storage_service_encryption_is_set_to_enabled_for_blob_service'] = storage_service_encryption_is_set_to_enabled_for_blob_service_3_2(storage_accounts)
    storage_results['storage_account_access_keys_are_periodically_regenerated'] = storage_account_access_keys_are_periodically_regenerated_3_2(activity_logs, storage_accounts, resource_groups)
    storage_results['public_access_level_is_set_to_private_for_blob_containers'] = public_access_level_is_set_to_private_for_blob_containers_3_6(storage_accounts)
    storage_results['storage_network_default_access_rule_set_to_deny'] = storage_network_default_access_rule_set_to_deny_3_7(storage_accounts)
    #storage_results['public_access_level_is_set_to_private_for_blob_containers'] = public_access_level_is_set_to_private_for_blob_containers_3_7(storage_accounts)
        
    with open(storage_accounts_filtered_path, 'w') as f:
        json.dump(storage_results, f, indent=4, sort_keys=True)
    return storage_results
