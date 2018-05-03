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

def secure_transfer_required_is_set_to_enabled_3_1(storage_accounts_list):
    set_count = 0
    not_set_count = 0
    filtered_list = []
    for account in storage_accounts_list:
        name = account['name']
        enabled = account['enableHttpsTrafficOnly']
        if enabled == True:
            set_count += 1
        else:
            not_set_count +=1
            filtered_list.append(name)
    stats = {'secure_transfer_required_is_set_to_enabled_failed_count': not_set_count, "secure_transfer_required_is_set_to_enabled_count": set_count}
    return filtered_list, stats   

def public_access_level_is_set_to_private_for_blob_containers_3_2(storage_accounts):
    unencrypted_blob_accounts = []
    stats = {}
    for account in storage_accounts:
        if account['encryption']['services']['blob']['enabled'] != True:
            unencrypted_blob_accounts.append(account['name'])

    stats = {'items_flagged': len(unencrypted_blob_accounts),
             'items_checked': len(storage_accounts)}

    return unencrypted_blob_accounts, stats  

def storage_service_encryption_is_set_to_enabled_for_file_service_3_6(storage_accounts_list):
    set_count = 0
    not_set_count = 0
    filtered_list = []
    for account in storage_account_list:
        file_service_name = account[0]
        enabled = account[1]
        if enabled == True:
            set_count += 1
        else:
            not_set_count +=1
            filtered_list.append(file_service_name)
    stats = {'encryption_not_set_count': not_set_count, "encryption_set_count": set_count}
    return filtered_list, stats


def storage_accounts_findings(storage_accounts):
    """
    Generate json for the storage_accounts findings
    """
    secure_transfer_required_is_set_to_enabled_3_1(storage_accounts_list)
    public_access_level_is_set_to_private_for_blob_containers_3_2(storage_accounts)
    

