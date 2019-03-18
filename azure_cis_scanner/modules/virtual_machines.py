import json
import os
import yaml

from azure.common.client_factory import get_client_from_cli_profile, get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from msrestazure.azure_active_directory import MSIAuthentication

from azure_cis_scanner import utils

filtered_virtual_machines_path = os.path.join(config['filtered_data_dir'], 'virtual_machines_filtered.json')
virtual_machines_path = os.path.join(config['raw_data_dir'], 'virtual_machines.json')
disks_path = os.path.join(config['raw_data_dir'], 'disks.json')
snapshots_path = os.path.join(config['raw_data_dir'], 'snapshots.json')
resource_groups_path = os.path.join(config['raw_data_dir'], "resource_groups.json")
credentials = config['cli_credentials']
sp_credentials = config['sp_credentials']
subscription_id=config['subscription_id']

def get_vms(sp_credentials, subscription_id=subscription_id):
    virtual_machines = []
    resource_groups = utils.load_resource_groups(resource_groups_path)
    compute = ComputeManagementClient(credentials, subscription_id)
    for resource_group in [x['name'] for x in resource_groups]:
        vms = compute.virtual_machines.list(resource_group)
        virtual_machines.extend(utils.get_list_from_paged_results(vms))
    with open(virtual_machines_path, 'w') as f:
        json.dump(virtual_machines, f, indent=4, sort_keys=True)
    return virtual_machines

def get_disks(disks_path):
    compute = ComputeManagementClient(sp_credentials, subscription_id)
    disks = compute.disks.list()
    
    disks = utils.get_list_from_paged_results(disks)
    with open(disks_path, 'w') as f:
        json.dump(disks, f, indent=4, sort_keys=True)
    return disks

def get_snapshots(snapshots_path):
    compute = ComputeManagementClient(sp_credentials, subscription_id)
    snaps = compute.snapshots.list()
    snaps = utils.get_list_from_paged_results(snaps)

    with open(snapshots_path, 'w') as f:
        json.dump(snaps, f, indent=4, sort_keys=True)
    return snaps

def get_virtual_machines(virtual_machines_path):
    """
    @virtual_machines_path: string - path to output json file
    @returns: list of virtual_machines dict
    """
    virtual_machines = json.loads(utils.call("az vm list"))
    for vm in virtual_machines:
        name = vm['name']
        resource_group = vm['resourceGroup']
        encrypted = utils.call("""az vm encryption show --name {name} 
            --resource-group {resource_group} 
            --query dataDisk""".format(name=name, resource_group=resource_group))
        if encrypted in ["", "Azure Disk Encryption is not enabled"]:
            vm['storageProfile']['dataDisksEncrypted'] = False
        else:
            vm['storageProfile']['dataDisksEncrypted'] = True
    
        if vm["networkProfile"]:
            ifaces = vm["networkProfile"]["networkInterfaces"]
            if ifaces:
                for iface in ifaces:
                    nic_name = iface['id'].split('/')[-1]
                    ifconfig = json.loads(utils.call("""az vm nic show -g {resource_group} 
                                --vm-name {vm_name} 
                                --nic {nic_name}""".format(resource_group=resource_group,                                               vm_name=name,
                                                          nic_name=nic_name)))
                    iface.update(ifconfig)
        # extensions = json.loads(utils.call("""az vm extension list 
        #         --vm-name {name} 
        #         --resource-group {resource_group}""".format(
        #             name=name,
        #             resource_group=resource_group))) 
        # vm['extensions'] = extensions

    with open(virtual_machines_path, 'w') as f:
        json.dump(virtual_machines, f, indent=4, sort_keys=True)
    return virtual_machines

def load_virtual_machines(virtual_machines_path):
    with open(virtual_machines_path, 'r') as f:
        virtual_machines = yaml.load(f, Loader=yaml.Loader)
    return virtual_machines

def load_disks(disks_path):
    with open(disks_path, 'r') as f:
        disks = yaml.load(f, Loader=yaml.Loader)
    return disks

def load_snapshots(snapshots_path):
    with open(snapshots_path, 'r') as f:
        snaps = yaml.load(f, Loader=yaml.Loader)
    return snaps

def get_data():
    get_virtual_machines(virtual_machines_path)
    # TODO switch to api below, but the datastructure is less detailed.  Trace cli call.
    #get_vms(virtual_machines_path)
    #get_snapshots(snapshots_path)
    #get_disks(disks_path)

def vm_agent_is_installed_7_1(virtual_machines):
    items_flagged_list = []
    for vm in virtual_machines:
        has_agent = False
        if vm['resources']:
            for resource in vm["resources"]:
                if ((vm['resources'][0]['virtualMachineExtensionType'] == 'MicrosoftMonitoringAgent') and (vm['resources'][0]['provisioningState'] == 'Succeeded')):
                    has_agent = True
        if has_agent:
            items_flagged_list.append((vm['resourceGroup'], vm['name']))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "vm_agent_is_installed",
                "negative_name": "",
                "columns": ["Resource Group", "Name"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def os_disk_is_encrypted_7_2(virtual_machines):
    items_flagged_list = []
    items_checked = 0
    for vm in virtual_machines:
        # lack of encryption is more severe if disks are not managed
        if vm['storageProfile']['osDisk']['managedDisk']:
            managed = "True"
        else:
            managed = "False"
        if vm['storageProfile']['osDisk']['encryptionSettings']:
            if not (vm['storageProfile']['osDisk']['encryptionSettings']['enabled'] == True):
                items_flagged_list.append((vm['resourceGroup'], 
                                           vm['name'], 
                                           vm['storageProfile']['osDisk']['name'],
                                           managed))
                items_checked += 1
        else:
            items_flagged_list.append((vm['resourceGroup'], 
                                       vm['name'], 
                                       vm['storageProfile']['osDisk']['name'],
                                       managed))
            items_checked += 1

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "os_disk_is_encrypted",
                "negative_name": "",
                "columns": ["Resource Group", "Name", "Disk Name", "Managed"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}


def data_disks_are_encrypted_7_3(virtual_machines):
    """
    TODO rather than making a second call here, enrich
    the data during the get_data phase if required.

    Then add the managed disk section commented out section.
    TODO: test this works for encrypted data disks.
    """
    items_flagged_list = []
    items_checked = 0

    # for vm in virtual_machines:
    #     name = vm['name']
    #     resource_group = vm['resourceGroup']
    #     encrypted = utils.call("az vm encryption show --name {name} --resource-group {resource_group} --query dataDisk".format(
    #         name=name, resource_group=resource_group))
    #     if encrypted in ["", "Azure Disk Encryption is not enabled"]:
    #         items_flagged_list.append((vm['resourceGroup'], vm['name'], "unknown"))
    for vm in virtual_machines:
        if not vm['storageProfile']['dataDisksEncrypted']:
            for disk in vm['storageProfile']['dataDisks']:
                if disk['managedDisk']:
                    managed = "True"
                else:
                    managed = "False"
                items_flagged_list.append((vm['resourceGroup'], vm['name'], disk['name'], managed))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "data_disks_are_encrypted",
                "negative_name": "",
                "columns": ["Resource Group", "Name", "Disk Name", "Managed"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

    # for disk in disks:
    #     if ('encryptionSettings' not in disk) or \
    #     (disk['encryptionSettings'] == None) or \
    #     (not disk['encryptionSettings']['enabled']):
    #         items_flagged_list.append((disk['location'], "unknown", disk['name']))

    # There doesn't seem to be encryption info in the snapshot.json
    # for snap in snapshots:
    #     if snap['encryptionSettings'] == None:
    #         items_flagged_list.append((disk['resourceGroup'], "unknown", disk['name']))


    stats = {'items_flagged': len(items_flagged_list), 
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "data_disks_are_encrypted",
                "negative_name": "",
                "columns": ["Resource Group", "Name", "Disk Name"]}
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}


def only_approved_extensions_are_installed_7_4(virtual_machines):
    # items in the following list do not imply failure, but require review
    items_flagged_list = []
    approved_extensions = [
        'AzureDiskEncryption',
        'IaaSAntimalware',
        'IaaSDiagnostics',
        'MicrosoftMonitoringAgent',
        'SqlIaaSAgent',
        'OmsAgentForLinux', 
        'VMAccessForLinux',
    ]
    for vm in virtual_machines:
        name = vm['name']
        resource_group = vm['resourceGroup']
        extensions = json.loads(utils.call("az vm extension list --vm-name {name} --resource-group {resource_group}".format(name=name,
            resource_group=resource_group)))
        for resource in vm["resources"]:
            extension_name = resource["id"].split('/')[-1]
            extension_names = []
            if extension_name not in approved_extensions:
                extension_names.append(extension_name)
            if extension_names:
                items_flagged_list.append((resource_group, name, extension['virtualMachineExtensionType']))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "only_approved_extensions_are_installed",
                "negative_name": "",
                "columns": ["Resource Group", "VM Name", "Extension Name"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def latest_patches_for_all_virtual_machines_are_applied_7_5(virtual_machines):
    pass

def endpoint_protection_for_all_virtual_machines_is_installed_7_6(virtual_machines):
    items_flagged_list = []
    accepted_protections = set(['EndpointSecurity', 'TrendMicroDSA', 'Antimalware', 'EndpointProtection','SCWPAgent', 'PortalProtectExtension', 'FileSecurity', 'IaaSAntimalware'])
    for vm in virtual_machines:
        name = vm['name']
        resource_group = vm['resourceGroup']
        extensions = json.loads(utils.call("az vm extension list --vm-name {name} --resource-group {resource_group}".format(name=name,
            resource_group=resource_group)))
        has_protection = False
        for extension in extensions:
            if set([extension['virtualMachineExtensionType']]).intersection(accepted_protections):
                has_protection = True
        if not has_protection:
            items_flagged_list.append((resource_group, name))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "endpoint_protection_for_all_virtual_machines_is_installed",
                "negative_name": "",
                "columns": ["Resource Group", "Name"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}


def test_controls():
    results = {}
    virtual_machines = load_virtual_machines(virtual_machines_path)
    #disks = load_disks(disks_path)
    #snapshots = load_snapshots(snapshots_path)
    results['vm_agent_is_installed'] = vm_agent_is_installed_7_1(virtual_machines)
    results['os_disk_is_encrypted'] = os_disk_is_encrypted_7_2(virtual_machines)
    results['data_disks_are_encrypted'] = data_disks_are_encrypted_7_3(virtual_machines)
    results['only_approved_extensions_are_installed'] = only_approved_extensions_are_installed_7_4(virtual_machines)
    results['endpoint_protection_for_all_virtual_machines_is_installed'] = endpoint_protection_for_all_virtual_machines_is_installed_7_6(virtual_machines)
    
    with open(filtered_virtual_machines_path, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)
    return results
