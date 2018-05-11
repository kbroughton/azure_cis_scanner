activity_logs_path = os.path.join(raw_data_dir, 'activity_logs.json')
storage_accounts_path = os.path.join(raw_data_dir, 'storage_accounts.json')
resource_groups_path = os.path.join(raw_data_dir, "resource_groups.json")

def get_storage_accounts(storage_accounts_path):
    """
    Query Azure api for storage accounts info and save to disk
    """
    storage_accounts = !az storage account list
    storage_accounts = yaml.load(storage_accounts.nlstr)
        
    with open(storage_accounts_path, 'w') as f:
        yaml.dump(storage_accounts, f)
    return storage_accounts

def load_storage_accounts(storage_accounts_path):
    with open(storage_accounts_path, 'r') as f:
        storage_accounts = yaml.load(f)
    return storage_accounts

activity_logs_starttime_timedelta = datetime.timedelta(days=90)
def get_start_time(timedelta=datetime.timedelta(days=90)):
    """
    Given datetime.timedelta(days=days, hours=hours), return string in iso tz format 
    """
    return datetime.datetime.strftime(datetime.datetime.now() - timedelta, "%Y-%m-%dT%H:%M:%SZ")

def get_activity_logs(activity_logs_path, resource_groups):
    activity_logs = {}
    start_time = get_start_time(activity_logs_starttime_timedelta)
    for resource_group in resource_groups:
        resource_group = resource_group['name']
        activity_log = !az monitor activity-log list --resource-group {resource_group} --start-time {start_time}
        activity_log = yaml.load(activity_log.nlstr)
        activity_logs[resource_group] = activity_log
    with open(activity_logs_path, 'w') as f:
        yaml.dump(activity_logs, f)
    return activity_logs    

def load_activity_logs(activity_logs_path):
    with open(activity_logs_path, 'r') as f:
        activity_logs = yaml.load(f)
    return activity_logs

def get_resource_groups(resource_groups_path):
    """
    @network_path: string - path to output json file
    """
    resource_groups = !az group list
    resource_groups = yaml.load(resource_groups.nlstr)
    with open(resource_groups_path, 'w') as f:
        yaml.dump(resource_groups, f)
    return resource_groups

def load_resource_groups(resource_groups_path):
    with open(resource_groups_path, 'r') as f:
        resource_groups = yaml.load(f)
    return resource_groups    

#################
# Tests
#################

def secure_transfer_required_is_set_to_enabled_3_1(storage_accounts):
    items_flagged_list = []
    for account in storage_accounts:
        name = account['name']
        enabled = account['enableHttpsTrafficOnly']
        if enabled != True:
            items_flagged_list.append(name)
    stats = {'items_flagged': len(items_flagged_list), "items_checked": len(storage_accounts)}
    return {"items": items_flagged_list, 
            "stats": stats, 
            "finding_name": "secure_transfer_required_is_set_to_enabled",
            "negative_name": "secure_transfer_required_not_enabled"}

def storage_service_encryption_is_set_to_enabled_for_blob_service_3_2(storage_accounts):
    items_flagged_list = []
    for account in storage_accounts:
        if account['encryption']['services']['blob'] and (account['encryption']['services']['blob']['enabled'] != True):
            items_flagged_list.append(account['name'])

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}
    metadata = {"finding_name": "storage_service_encryption_is_set_to_enabled_for_blob_service",
                "negative_name": "storage_service_encryption_not_enabled_for_blob_service"}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata }
           

# may need to run section 6 Networking first to get activity_log
def storage_account_access_keys_are_periodically_regenerated_3_3(activity_logs, storage_accounts, resource_groups):
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
        items_flagged_list.append((resource_group, storage_account, str(most_recent_rotations.get(storage_account_name, "No rotation"))))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}
    metadata = {"finding_name": "storage_account_access_keys_are_periodically_regenerated",
                "negative_name": "storage_account_access_keys_not_periodically_regenerated" }
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

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
                                      
def storage_service_encryption_is_set_to_enabled_for_file_service_3_6(storage_accounts):
    items_flagged_list = []
    stats = {}
    for account in storage_accounts:
        if account['encryption']['services']['file'] and (account['encryption']['services']['file']['enabled'] != True):
            items_flagged_list.append(account['name'])

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}
    metadata = {"finding_name": "storage_service_encryption_is_set_to_enabled_for_file_service",
                "negative_name": "storage_service_encryption_not_enabled_for_file_service"}

    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def public_access_level_is_set_to_private_for_blob_containers_3_7(storage_accounts):
    items_flagged_list = []
    items_checked = 0
    for account in storage_accounts:
        account_name = account["name"]
        resource_group = account["resourceGroup"]
        # get a key that works.  likely this will be a specific key not key[0]
        keys = !az storage account keys list --account-name {account_name} --resource-group {resource_group}
        keys = yaml.load(keys.nlstr)
        key = keys[0]
        container_list = !az storage container list --account-name {account_name} --account-key {account_key}
        container_list = yaml.load(container_list.nlstr)
        for container in container_list:
            print(container)
            items_checked += 1
            public_access = container["properties"]["public_access"]
            if public_access == True:
                items_flagged_list.append(container)
    stats = {'items_flagged': len(items_flagged_list), "items_checked": items_checked}
    metadata = {"finding_name": "public_access_level_is_set_to_private_for_blob_containers",
                "negative_name": "public_access_level_not_private_for_blob_containers"}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata }

    
def get_data():
    """
    Generate json for the storage_accounts findings
    """
    resource_groups = get_resource_groups(resource_groups_path)
    get_activity_logs(activity_logs_path, resource_groups)
    get_storage_accounts(storage_accounts_path)

def run_tests():
    """
    Generate filtered (failing) output in json
    """
    resource_groups = load_resource_groups(resource_groups_path)
    storage_accounts = load_storage_accounts(storage_accounts_path)
    activity_logs = load_activity_logs(activity_logs_path)
    
    storage_results = {}
    storage_results['secure_transfer_required_is_set_to_enabled'] = secure_transfer_required_is_set_to_enabled_3_1(storage_accounts)
    storage_results['storage_service_encryption_is_set_to_enabled_for_blob_service'] = storage_service_encryption_is_set_to_enabled_for_blob_service_3_2(storage_accounts)
    storage_results['storage_account_access_keys_are_periodically_regenerated'] = storage_account_access_keys_are_periodically_regenerated_3_3(activity_logs, storage_accounts, resource_groups)
    storage_results['storage_service_encryption_is_set_to_enabled_for_file_service'] = storage_service_encryption_is_set_to_enabled_for_file_service_3_6(storage_accounts)
    #storage_results['public_access_level_is_set_to_private_for_blob_containers'] = public_access_level_is_set_to_private_for_blob_containers_3_7(storage_accounts)
        
    with open(os.path.join(scan_data_dir, 'filtered', 'storage_accounts_filtered.json'), 'w') as f:
        json.dump(storage_results, f, indent=4, sort_keys=True)
    return storage_results
