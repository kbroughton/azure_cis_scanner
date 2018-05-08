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
            "name": "secure_transfer_required_is_set_to_enabled_3_1",
            "file_name": "secure_transfer_required_not_enabled"}

def storage_service_encryption_is_set_to_enabled_for_blob_service_3_2(storage_accounts):
    items_flagged_list = []
    for account in storage_accounts:
        if account['encryption']['services']['blob'] and (account['encryption']['services']['blob']['enabled'] != True):
            items_flagged_list.append(account['name'])

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}

    return {"items": items_flagged_list, 
            "stats": stats,
            "name": "storage_service_encryption_is_set_to_enabled_for_blob_service_3_2",
            "file_name": "storage_service_encryption_not_enabled_for_blob_service"}

# may need to run section 6 Networking first to get activity_log
def storage_account_access_keys_are_periodically_regenerated_3_3(activity_log, storage_accounts, resource_groups):
    items_flagged_list = []
    
    max_rotation_days = 90
    most_recent_rotations = {}
    for log in activity_log:
        if log["authorization"]["action"] == "Microsoft.Storage/storageAccounts/regenerateKey/action":
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
        items_flagged_list.append((resource_group, storage_account, str(most_recent_rotations.get(storage_account, "No rotation"))))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(storage_accounts)}

    return {"items": items_flagged_list, 
            "stats": stats,
            "name": "storage_account_access_keys_are_periodically_regenerated_3_3",
            "file_name": "storage_account_access_keys_not_periodically_regenerated"}

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
             'items_checked': len(storage_accounts),
             "name": "storage_service_encryption_is_set_to_enabled_for_file_service_3_6",
             "file_name": "storage_service_encryption_not_enabled_for_file_service"}

    return {"items": items_flagged_list, "stats": stats}

def public_access_level_is_set_to_private_for_blob_containers_3_7(storage_accounts):
    items_flagged_list = []
    items_checked = 0
    for account in storage_accounts:
        account_name = account["name"]
        resource_group = account["resoureGroup"]
        # get a key that works.  likely this will be a specific key not key[0]
        keys = !az storage account keys list --account-name {account_name} --resource-group {resource_group}
        keys = yaml.load(keys.nlstr)
        key = keys[0]
        container_list = !az storage container list --account-name {account_name} --account-key {account_key}
        container_list = yaml.load(container_list.nlstr)
        for container in container_list:
            items_checked += 1
            public_access = container["properties"]["public_access"]
            if public_access == True:
                items_flagged_list.append(container)
    stats = {'items_flagged': len(items_flagged_list), "items_checked": items_checked}
    return {"items": items_flagged_list, 
            "stats": stats,
            "name": "public_access_level_is_set_to_private_for_blob_containers_3_7",
            "file_name": "public_access_level_not_private_for_blob_containers"}
                                      
def storage_accounts_findings(storage_accounts):
    """
    Generate json for the storage_accounts findings
    """
    tests = [
        secure_transfer_required_is_set_to_enabled_3_1,
        storage_service_encryption_is_set_to_enabled_for_blob_service_3_2,
        storage_account_access_keys_are_periodically_regenerated_3_3,
        storage_service_encryption_is_set_to_enabled_for_file_service_3_6
    ]
    storage_results = []
    for test in tests:
        storage_results.append(test.__call__(storage_accounts))
    
    return storage_results
    
