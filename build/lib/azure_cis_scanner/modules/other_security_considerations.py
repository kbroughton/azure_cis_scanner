import os
import yaml

keyvaults_path = os.path.join(raw_data_dir, 'keyvaults.json')
keyvault_keys_and_secrets_metadata_path = os.path.join(raw_data_dir, 'keyvault_keys_and_secrets_metadata.json')
locked_resources_path = os.path.join(raw_data_dir, 'locked_resources.json')
other_security_considerations_filtered_path = os.path.join(filtered_data_dir, 'other_security_considerations_filtered.json')

def get_keyvaults(keyvaults_path):
    """
    @keyvaults_path: string - path to output json file
    @returns: list of virtual_machines dict
    """
    keyvaults = !az keyvault list
    keyvaults = yaml.load(keyvaults.nlstr)
    with open(keyvaults_path, 'w') as f:
        json.dump(keyvaults, f, indent=4, sort_keys=True)
    return keyvaults

def load_keyvaults(keyvaults_path):
    with open(keyvaults_path, 'r') as f:
        keyvaults = yaml.load(f)
    return keyvaults

def get_locked_resources():
    lock_list = !az lock list
    lock_list = yaml.load(lock_list.nlstr)

    with open(locked_resources_path, 'w') as f:
        json.dump(lock_list, f, indent=4, sort_keys=True)
    return lock_list

def load_locked_resources(locked_resources_path):
    with open(locked_resources_path, 'r') as f:
        locked_list = yaml.load(f)
    return locked_list

def get_keyvault_keys_and_secrets_metadata(keyvault_keys_and_secrets_metadata_path, keyvaults):
    metadata = {}
    for keyvault in keyvaults:        
        vault_name = keyvault['name']
        metadata[vault_name] = {}
        keys = !az keyvault key list --vault-name {vault_name}
        keys = yaml.load(keys.nlstr)
        metadata[vault_name]['keys'] = keys
        secrets = !az keyvault secret list --vault-name {vault_name}
        secrets = yaml.load(secrets.nlstr)
        metadata[vault_name]['secrets'] = secrets
    
    with open(keyvault_keys_and_secrets_metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4, sort_keys=True)
    return metadata

def load_keyvault_keys_and_secrets_metadata(keyvault_keys_and_secrets_metadata_path):
    with open(keyvault_keys_and_secrets_metadata_path, 'r') as f:
        metadata = yaml.load(f)
    return metadata

def get_data():
    keyvaults = get_keyvaults(keyvaults_path)
    get_keyvault_keys_and_secrets_metadata(keyvault_keys_and_secrets_metadata_path, keyvaults)
    get_locked_resources()

MAX_EXPIRY_ROTATION_DAYS = 730
# 8.1 and 8.2
def expiry_date_is_set_on_all_keys_and_secrets(keyvault_keys_and_secrets_metadata):
    items_flagged_list = []
    items_checked = 0
    today = datetime.datetime.today()
    
    def get_key_or_secret_status(info):
        enabled = info['attributes']['enabled']
        created = datetime.datetime.strptime(info['attributes']['created'].split('T')[0], '%Y-%m-%d')
        expires = info['attributes']['expires']
        status = "ok"
        if expires:
            expires = datetime.datetime.strptime(expires.split('T')[0], '%Y-%m-%d')
            expiry_delta = expires - created
            if today > expires:
                satus = "expired"
            elif expiry_delta > datetime.timedelta(days=MAX_EXPIRY_ROTATION_DAYS):
                status = "exceeds max expiry days"
            # convert times back to a string for display
            expires = expires.strftime('%Y-%m-%d')
        else:
            status = "no expiry"
            expires = "None"
        created = created.strftime('%Y-%m-%d')            
            
        return status, created, expires
    
    for keyvault_name, metadata in keyvault_keys_and_secrets_metadata.items():
        for key_info in metadata['keys']:
            items_checked += 1
            if "ERROR" in key_info:
                print("ERROR", metadata['keys']["ERROR"])
                items_flagged_list.append((keyvault_name, "ACCESS_DENIED", "key", "N/A", "N/A", "N/A"))
                continue
            key_name = key_info['kid'].split('/')[-1]
            status, created, expires = get_key_or_secret_status(key_info)
            if status != "ok":
                items_flagged_list.append((keyvault_name, key_name, "key", status, created, expires))
                
        for secret_info in metadata['secrets']:
            items_checked += 1
            if "ERROR" in secret_info:
                print("ERROR",  metadata['secrets']["ERROR"])
                items_flagged_list.append((keyvault_name, "ACCESS_DENIED", "secret", "N/A", "N/A", "N/A"))
                continue
            secret_name = secret_info['id'].split('/')[-1]
            status, created, expires = get_key_or_secret_status(secret_info)                
            if status != "ok":
                items_flagged_list.append((keyvault_name, secret_name, "secret", status, created, expires))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': items_checked}
    metadata = {"finding_name": "expiry_date_is_set_on_all_keys_and_secrets",
                "negative_name": "",
                "columns": ["KeyVault Name", "Name", "Type", "Status", "Created", "Expires"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

critical_resources_list = []
def resource_locks_are_set_for_mission_critical_azure_resources_8_3(critical_resources_list, locked_resources):
    """
    This finding needs some work.
    It is not clear from `az lock list` what resource is being locked.
    For now, best ignore comparison and flag an error if len(critical_resources_list) < len(locked_resources)
    """
    items_flagged_list = []
    critical_resources = set(critical_resources_list)
    if len(locked_resources) == 0 and len(critical_resources_list) == 0:
        stats = {'items_flagged': 1,
                 'items_checked': 1}
    else:
        stats = {'items_flagged': len(critical_resources_list) - len(locked_resources),
                 'items_checked': len(critical_resources_list)}
        # This is really the inverse of the usual items flagged list
        #items_flagged_list = list(critical_resources.intersection(set(locked_resources)))
        items_flagged_list = [(x['name'], x['id'], x['notes']) for x in locked_resources]
    metadata = {"finding_name": "resource_locks_are_set_for_mission_critical_Azure_resources",
                "negative_name": "",
                "columns": ["Lock Name", "Lock ID", "Notes"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def test_controls():
    keyvault_keys_and_secrets_metadata = load_keyvault_keys_and_secrets_metadata(keyvault_keys_and_secrets_metadata_path)
    locked_resources = load_locked_resources(locked_resources_path)
    results = {}
    results['expiry_date_is_set_on_all_keys_and_secrets'] = expiry_date_is_set_on_all_keys_and_secrets(keyvault_keys_and_secrets_metadata)
    results['resource_locks_are_set_for_mission_critical_azure_resources'] = resource_locks_are_set_for_mission_critical_azure_resources_8_3(critical_resources_list, locked_resources)
    
    with open(other_security_considerations_filtered_path, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)
    return results