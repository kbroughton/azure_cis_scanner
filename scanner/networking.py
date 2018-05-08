import ./utils.py

##########################
# Get Raw Data
##########################

network_flows_path = os.path.join(raw_data_dir, "network_flows.json")
resource_groups_path = os.path.join(raw_data_dir, "resource_groups.json")

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

network_security_groups_path = os.path.join(raw_data_dir, "network_security_groups.json")

def get_network_security_groups(network_security_groups_path):
    """
    @network_path: string - path to output json file
    """
    network_security_groups = !az network nsg list
    network_security_groups = yaml.load(network_security_groups.nlstr)
    with open(network_security_groups_path, 'w') as f:
        yaml.dump(network_security_groups, f)
    return network_security_groups

def load_network_security_groups(network_security_groups_path):
    with open(network_security_groups_path, 'r') as f:
        network_security_groups = yaml.load(f)
    return network_security_groups

network_watcher_path = os.path.join(raw_data_dir, "network_watcher.json")
approved_regions = []
def get_network_watcher(network_watcher_path):
    """
    @network_watcher_path: string - path to output json file
    """
    network_watcher = !az network watcher list
    network_watcher = yaml.load(network_watcher.nlstr)
    with open(network_watcher_path, 'w') as f:
        yaml.dump(network_watcher, f)
    return network_watcher

def load_network_watcher(network_watcher_path):
    with open(network_watcher_path, 'r') as f:
        network_watcher = yaml.load(f)
    return network_watcher

def get_network_flows(network_flows_path, network_security_groups):
    """
    @network_flows_path: string - path to output json file
    @network_security_groups: list of nsgs
    @returns: list of network flow dicts
    """
    network_flows = []
    for nsg in network_security_groups:
        resource_group = nsg['resourceGroup']
        nsg_id = nsg['id']
        network_flow = !az network watcher flow-log show --resource-group {resource_group} --nsg {nsg_id}
        network_flow = yaml.load(network_flow.nlstr)
        nsg_name = nsg["name"]
        network_flows.append({"resource_group": resource_group, "nsg_name": nsg_name, "network_flow": network_flow})
        
    with open(network_flows_path, 'w') as f:
        yaml.dump(network_flows, f)
    return network_flows

def load_network_flows(network_flows_path):
    with open(network_flows_path, 'r') as f:
        network_flows = yaml.load(f)
    return network_flows

##########################
# Tests
##########################

def network_watcher_is_enabled_6_5(network_watcher):
    network_watcher_is_enabled_failed = []    
    for watcher in network_watcher:
        if watcher['provisioningState'] != 'Succeeded':
            network_watcher_is_enabled_failed.append(watcher)
            
    print("Praetorian found that {} of {} network watchers were not enabled".format(len(network_watcher_is_enabled_failed), len(network_watcher)))

    return network_watcher_is_enabled_failed

# 6.1, 6.2, 
access_is_restricted_from_the_internet_path = os.path.join(filtered_data_dir, "access_is_restricted_from_the_internet.json")
def access_is_restricted_from_the_internet_6_1(network_security_groups, 
                                               rdp_access_is_restricted_from_the_internet_path):
    items_flagged_list = []
    for nsg in network_security_groups:
        # should actually be any port range that includes 3389
        security_rules = nsg['securityRules']
        for security_rule in security_rules:
            if security_rule['destinationPortRange'] == '3389' and security_rule['direction'] == 'Inbound' and security_rule['protocol'] == 'TCP':
                if security_rule['sourceAddressPrefix'] in ['*', '/0', 'internet', 'any']:
                    items_flagged_list.append((nsg['resourceGroup'],nsg['name'], '3389', security_rule))
            if security_rule['destinationPortRange'] == '22' and security_rule['direction'] == 'Inbound':
                if security_rule['sourceAddressPrefix'] in ['*', '/0', 'internet', 'any']:
                    items_flagged_list.append((nsg['resourceGroup'],nsg['name'], '22', security_rule))
                    
    with open(rdp_access_is_restricted_from_the_internet_path, 'w') as f:
        yaml.dump(items_flagged_list, f)
    stats = {'items_flagged': len(items_flagged_list), 'items_checked': len(network_flows), 
             'columns': ['resource_group', 'nsg_name', 'port', 'security_rule']}
    return items_flagged_list, stats

def sql_server_access_is_restricted_from_the_internet_6_3():
    """
    Powershell
    """
    pass                

def network_security_group_flow_log_retention_period_is_greater_than_90_days_6_4(network_flows):
    items_flagged_list = []
    for network_flow in network_flows:
        flow = network_flow['network_flow']
        if flow['enabled'] == False:
            status = "Not enabled"
            items_flagged_list.append((network_flow['resource_group'], network_flow['nsg_name'], status))
        elif flow['retentionPolicy']['days'] == 0:
            continue
        elif (flow['retentionPolicy']['days'] < 90) or (flow['retentionPolicy']['enabled'] == False):
            status("Days {}, Enabled {}".format(flow['retentionPolicy']['days'], flow['retentionPolicy']['enabled']))
            items_flagged_list.append((network_flow['resource_group'], network_flow['nsg_name'], status))
    stats = {'items_flagged': len(items_flagged_list), 'items_checked': len(network_flows)}
    return items_flagged_list, stats