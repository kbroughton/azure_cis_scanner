import os
import yaml

filtered_virtual_machines_path = os.path.join(filtered_data_dir, 'virtual_machines_filtered.json')
virtual_machines_path = os.path.join(raw_data_dir, 'virtual_machines.json')

def get_virtual_machines(virtual_machines_path):
    """
    @virtual_machines_path: string - path to output json file
    @returns: list of virtual_machines dict
    """
    virtual_machines = !az vm list
    virtual_machines = yaml.load(virtual_machines.nlstr)
    with open(virtual_machines_path, 'w') as f:
        json.dump(virtual_machines, f, indent=4, sort_keys=True)
    return virtual_machines

def load_virtual_machines(virtual_machines_path):
    with open(virtual_machines_path, 'r') as f:
        virtual_machines = yaml.load(f)
    return virtual_machines

def get_data():
    get_virtual_machines(virtual_machines_path)

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
        if vm['storageProfile']['osDisk']['encryptionSettings']:
            if not (vm['storageProfile']['osDisk']['encryptionSettings']['enabled'] == True):
                items_flagged_list.append((vm['resourceGroup'], vm['name'], vm['storageProfile']['osDisk']['name']))
                items_checked += 1
        else:
            items_flagged_list.append((vm['resourceGroup'], vm['name'], vm['storageProfile']['osDisk']['name']))
            items_checked += 1

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "os_disk_is_encrypted",
                "negative_name": "",
                "columns": ["Resource Group", "Name", "Disk Name"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def data_disks_are_encrypted_7_3(virtual_machines):
    items_flagged_list = []
    items_checked = 0
    for vm in virtual_machines:
        name = vm['name']
        resource_group = vm['resourceGroup']
#         encrypted = !az vm encryption show --name {name} --resource-group {resource_group} --query dataDisk
#         encrypted = yaml.load(encrypted.nlstr)
#         if encrypted != "Encrypted":
#             items_flagged_list.append((vm['resourceGroup'], vm['name']))
        for disk in vm['storageProfile']['dataDisks']:
            if disk['encryptionSettings'] == None:
                items_flagged_list.append((vm['resourceGroup'], vm['name'], disk['name']))

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
        extensions = !az vm extension list --vm-name {name} --resource-group {resource_group}
        extensions = yaml.load(extensions.nlstr)
        for extension in extensions:
            if extension['virtualMachineExtensionType'] not in approved_extensions:
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
#         endpoint_protection = !az vm show --resource-group {resource_group} --name {name} -d
#         endpoint_protection = yaml.load(endpoint_protection.nlstr)
        extensions = !az vm extension list --vm-name {name} --resource-group {resource_group}
        extensions = yaml.load(extensions.nlstr)
        has_protection = False
        for extension in extensions:
            if set([extension['virtualMachineExtensionType']]).intersection(accepted_protections):
                has_protection = True
        if not has_protection:
            items_flagged_list.append((resource_group, name, extension.get('virtualMachineExtensionType', "No extension")))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(virtual_machines)}
    metadata = {"finding_name": "endpoint_protection_for_all_virtual_machines_is_installed",
                "negative_name": "",
                "columns": ["Resource Group", "Name", "Unapproved Extension"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}


def test_controls():
    results = {}
    virtual_machines = load_virtual_machines(virtual_machines_path)
    results['vm_agent_is_installed'] = vm_agent_is_installed_7_1(virtual_machines)
    results['os_disk_is_encrypted'] = os_disk_is_encrypted_7_2(virtual_machines)
    results['data_disks_are_encrypted'] = data_disks_are_encrypted_7_3(virtual_machines)
    results['only_approved_extensions_are_installed'] = only_approved_extensions_are_installed_7_4(virtual_machines)
    results['endpoint_protection_for_all_virtual_machines_is_installed'] = endpoint_protection_for_all_virtual_machines_is_installed_7_6(virtual_machines)
    
    with open(filtered_virtual_machines_path, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)
    return results