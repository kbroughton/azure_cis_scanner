
import datetime
import json
import os
import traceback
import yaml

from azure.mgmt.network import NetworkManagementClient

from azure_cis_scanner import utils
from azure_cis_scanner.utils import get_list_from_paged_results, AzScannerException

resource_groups_path = os.path.join(config['raw_data_dir'], "resource_groups.json")
network_flows_path = os.path.join(config['raw_data_dir'], "network_flows.json")
network_watcher_path = os.path.join(config['raw_data_dir'], "network_watcher.json")
networking_filtered_path = os.path.join(config['filtered_data_dir'], 'networking_filtered.json')
network_security_groups_path = os.path.join(config['raw_data_dir'], "network_security_groups.json")
resource_providers_path = os.path.join(config['raw_data_dir'], "resource_providers.json")
credentials = config['cli_credentials']
subscription_id = config['subscription_id']
NETWORK_FLOWS = True

##########################
# Get Raw Data
##########################

def get_data():
    network_security_groups = get_network_security_groups(network_security_groups_path)
    network_watcher = get_network_watcher(network_watcher_path)
    resource_providers = get_resource_providers(resource_providers_path)
    try:
        get_network_flows(network_flows_path, network_security_groups, network_watcher)
    except Exception as e:
            print("Exception was thrown! Unable to get network watcher flows.  Check permissions.")
            print(e)
            print(traceback.format_exc())
            NETWORK_FLOWS = False

def get_resource_providers(resource_providers_path):
    resource_providers = json.loads(utils.call("az provider list"))
    with open(resource_providers_path, 'w') as f:
        json.dump(resource_providers, f, indent=4, sort_keys=True)
    return resource_providers

def load_resource_providers(resource_providers_path):
    with open(resource_providers_path, 'r') as f:
        resource_providers = yaml.load(f, Loader=yaml.Loader)
    return resource_providers

def get_network_security_groups(network_security_groups_path):
    """
    @network_path: string - path to output json file
    """
    network_security_groups = json.loads(utils.call("az network nsg list"))
    with open(network_security_groups_path, 'w') as f:
        json.dump(network_security_groups, f, indent=4, sort_keys=True)
    return network_security_groups

def load_network_security_groups(network_security_groups_path):
    with open(network_security_groups_path, 'r') as f:
        network_security_groups = yaml.load(f, Loader=yaml.Loader)
    return network_security_groups

approved_regions = []
def get_network_watcher(network_watcher_path):
    """
    @network_watcher_path: string - path to output json file
    """
    network_watcher = json.loads(utils.call("az network watcher list"))
    with open(network_watcher_path, 'w') as f:
        json.dump(network_watcher, f, indent=4, sort_keys=True)
    return network_watcher

def load_network_watcher(network_watcher_path):
    with open(network_watcher_path, 'r') as f:
        network_watcher = yaml.load(f, Loader=yaml.Loader)
    return network_watcher

def get_network_flows(network_flows_path, network_security_groups, network_watcher):
    """
    @network_flows_path: string - path to output json file
    @network_security_groups: list of nsgs
    @network_watcher: list of network watchers per location/resource group
    @returns: list of network flow dicts
    """
    network_flows = []
    for nsg in network_security_groups:
        resource_group = nsg['resourceGroup']
        nsg_id = nsg['id']
        nsg_name = nsg["name"]
        network_flow = {}
        rg_has_watcher = False
        for item in network_watcher:
            if item['resourceGroup'] == resource_group:
                rg_has_watcher = True
                break
        if rg_has_watcher:
            try:
                print("getting flow for nsg {}".format(nsg_name))
                network_flow = utils.call("az network watcher flow-log show --resource-group {resource_group} --nsg {nsg_id}".format(
                    resource_group=resource_group, nsg_id=nsg_id))
                network_flow = json.loads(network_flow)
                network_flows.append({"resource_group": resource_group, "nsg_name": nsg_name, "network_flow": network_flow})
            except Exception as e:
                print("Exception was thrown! Unable to get network watcher flows for {}.  Check permissions.".format(nsg_name))
                print("exception:", e)
                print(traceback.format_exc()) 
        else: 
            #out.find("network watcher is not enabled for region") != -1:
                print("Network flow not enabled for {}.".format(nsg_name))
                network_flows.append({"resource_group": resource_group, "nsg_name": nsg_name, "network_flow": {"enabled": False}})                       
            
    with open(network_flows_path, 'w') as f:
        json.dump(network_flows, f, indent=4, sort_keys=True)
    return network_flows

def load_network_flows(network_flows_path):
    with open(network_flows_path, 'r') as f:
        network_flows = yaml.load(f, Loader=yaml.Loader)
    return network_flows

##########################
# Tests
##########################

def test_controls():
    """
    Generate filtered (failing) output in json
    """
    network_watcher = load_network_watcher(network_watcher_path)
    network_security_groups = load_network_security_groups(network_security_groups_path)
    resource_groups = utils.load_resource_groups(resource_groups_path)
    network_flows = load_network_flows(network_flows_path)
    resource_providers = load_resource_providers(resource_providers_path)
    networking_results = {}

    networking_results['access_is_restricted_from_the_internet'] = access_is_restricted_from_the_internet_6_1(network_security_groups)
    networking_results['network_security_group_flow_log_retention_period_is_greater_than_90_days'] = network_security_group_flow_log_retention_period_is_greater_than_90_days_6_4(network_flows)
    networking_results['network_watcher_is_enabled'] = network_watcher_is_enabled_6_5(network_watcher, resource_providers)
                
    with open(networking_filtered_path, 'w') as f:
        json.dump(networking_results, f, indent=4, sort_keys=True)
    return networking_results

# 6.1, 6.2, 
def access_is_restricted_from_the_internet_6_1(network_security_groups):
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
                    items_flagged_list.append((nsg['resourceGroup'],nsg['name'], '22', security_rule['name']))
                    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(network_security_groups)}
    metadata = {"finding_name": "access_is_restricted_from_the_internet",
                "negative_name": "",
                "columns": ["Resource Group", "NSG", "Port", "Rule"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}


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

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(network_flows)}
    metadata = {"finding_name": "network_security_group_flow_log_retention_period_is_greater_than_90_days",
                "negative_name": "",
                "columns": ["Resource Group", "Network Flow", "Status"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def get_watcher_locations(resource_providers):
    for provider in resource_providers:
        if provider["namespace"] == "Microsoft.Network":
            for resource_type in provider["resourceTypes"]:
                if resource_type['resourceType'] == "networkWatchers":
                    return resource_type

def network_watcher_is_enabled_6_5(network_watcher, resource_providers):
    """
    It is not entirely clear how this should work.
    A network watcher should be enabled in all regions.
    If there are multiple network watchers, the union of all their
    locations should cover all possible watcher locations as defined by resource_providers

    """
    watcher_locations = get_watcher_locations(resource_providers)
    all_locations = set([x.replace(' ', '').lower() for x in watcher_locations['locations']])
    print("all_locations", all_locations)
    covered_locations = set({})
    for watcher in network_watcher:
        if watcher['provisioningState'] != 'Succeeded':
            covered_locations.add(watcher['location'])

    items_flagged_list = list(all_locations.difference(covered_locations))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(all_locations)}
    metadata = {"finding_name": "network_watcher_is_enabled",
                "negative_name": "",
                "columns": ["Location"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}
