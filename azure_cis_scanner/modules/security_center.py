#%load {scanner_dir}/scanner/modules/security_center.py
import yaml
import os
import json
from azure_cis_scanner import utils

import azurerm
from azure.common.client_factory import get_client_from_cli_profile, get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from msrestazure.azure_active_directory import MSIAuthentication

security_center_filtered_path = os.path.join(config['filtered_data_dir'], 'security_center_filtered.json')
security_center_path = os.path.join(config['raw_data_dir'], "security_center.json")
subscription_id = config['subscription_id']


def get_security_center(security_center_path):
    """
    Query Azure api for storage accounts info and save to disk
    """

    headers = {"Content-Type": "application/json"} 
    url = "https://management.azure.com/subscriptions/{subscription_id}/providers/microsoft.Security/policies?api-version=2015-06-01-preview".format(subscription_id=subscription_id)

    security_center = json.loads(utils.make_request(url, headers=headers))
    print("get_security_center {}".format(security_center))
    security_center = security_center.get('value', [])
        
    with open(security_center_path, 'w') as f:
        yaml.dump(security_center, f)
    return security_center

def load_security_center(security_center_filtered_path):
    with open(security_center_path, 'r') as f:
        security_center = yaml.load(f, Loader=yaml.Loader)
    return security_center

def get_data():
    """
    Generate json for the security_center findings
    """
    get_security_center(security_center_path)

def test_controls():
    """
    Generate filtered (failing) output in json
    """
    security_center = load_security_center(security_center_path)
    security_center_results = {}

    security_center_results['standard_pricing_tier_is_selected'] = standard_pricing_tier_is_selected_2_1(security_center)
    security_center_results['automatic_provisioning_of_monitoring_agent_is_set_to_on'] = automatic_provisioning_of_monitoring_agent_is_set_to_on_2_2(security_center)
    security_center_results['system_updates_is_set_to_on'] = system_updates_is_set_to_on_2_3(security_center)
    security_center_results['security_configurations_is_set_to_on'] = security_configurations_is_set_to_on_2_4(security_center)
    security_center_results['endpoint_protection_is_set_to_on'] = endpoint_protection_is_set_to_on_2_5(security_center)
    security_center_results['disk_encryption_is_set_to_on'] = disk_encryption_is_set_to_on_2_6(security_center)
    security_center_results['network_security_groups_is_set_to_on'] = network_security_groups_is_set_to_on_2_7(security_center)
    security_center_results['web_application_firewall_is_set_to_on'] = web_application_firewall_is_set_to_on_2_8(security_center)
    security_center_results['next_generation_firewall_is_set_to_on'] = next_generation_firewall_is_set_to_on_2_9(security_center)
    security_center_results['vulnerability_assessment_is_set_to_on'] = vulnerability_assessment_is_set_to_on_2_10(security_center)
    security_center_results['storage_encryption_is_set_to_on'] = storage_encryption_is_set_to_on_2_11(security_center)
    security_center_results['just_in_time_access_is_set_to_on'] = just_in_time_access_is_set_to_on_2_12(security_center)
    security_center_results['adaptive_application_controls_is_set_to_on'] = adaptive_application_controls_is_set_to_on_2_13(security_center)
    security_center_results['sql_auditing_and_threat_detection_is_set_to_on'] = sql_auditing_and_threat_detection_is_set_to_on_2_14(security_center)
    security_center_results['sql_encryption_is_set_to_on'] = sql_encryption_is_set_to_on_2_15(security_center)
    security_center_results['security_contact_emails_is_set'] = security_contact_emails_is_set_2_16(security_center)
    security_center_results['security_contact_phone_number_is_set'] = security_contact_phone_number_is_set_2_17(security_center)
    security_center_results['send_me_emails_about_alerts_is_set_to_on'] = send_me_emails_about_alerts_is_set_to_on_2_18(security_center)
    security_center_results['send_email_also_to_subscription_owners_is_set_to_on'] = send_email_also_to_subscription_owners_is_set_to_on_2_19(security_center)
                
    with open(security_center_filtered_path, 'w') as f:
        json.dump(security_center_results, f, indent=4, sort_keys=True)
    return security_center_results

def standard_pricing_tier_is_selected_2_1(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        pricing_configuration = item['properties']['pricingConfiguration']
        pricing_tier = pricing_configuration['selectedPricingTier']
        active = pricing_configuration['active']
        if (pricing_tier == "Free") or (active != "On"):
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "standard_pricing_tier_is_selected",
                "negative_name": "standard_pricing_tier_not_selected",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}  

def automatic_provisioning_of_monitoring_agent_is_set_to_on_2_2(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        automatic_provisioning_of_monitoring_agent = item['properties']['logCollection']
        if automatic_provisioning_of_monitoring_agent != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "automatic_provisioning_of_monitoring_agent_is_set_to_on",
                "negative_name": "automatic_provisioning_of_monitoring_agent_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}
    
def system_updates_is_set_to_on_2_3(security_center):
    """
    New query param in 1.1 is properties.parameters.systemUpdatesMonitoringEffect
    but it is not in the output of the general api call.  Nor in az policy definition list.
    """
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        system_updates = item['properties']['recommendations']['patch']
        if system_updates != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "system_updates_is_set_to_on",
                "negative_name": "system_updates_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}    


def monitor_os_vulnerabilities_is_set_to_on_2_4b(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        security_configurations = item['properties']['parameters']['systemConfigurationsMonitoringEffect']
        if security_configurations not in ["Disabled", None]:
            items_flagged_list.append((resource_group))
            
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "monitor_os_vulnerabilities_is_set_to_on",
                "negative_name": "monitor_os_vulnerabilities_disabled",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata} 

def security_configurations_is_set_to_on_2_4(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        security_configurations = item['properties']['recommendations']['baseline']
        if security_configurations != "On":
            items_flagged_list.append((resource_group))
            
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "security_configurations_is_set_to_on",
                "negative_name": "security_configurations_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata} 

def endpoint_protection_is_set_to_on_2_5(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        endpoint_protection = item['properties']['recommendations']['antimalware']
        if endpoint_protection != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "endpoint_protection_is_set_to_on",
                "negative_name": "endpoint_protection_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def disk_encryption_is_set_to_on_2_6(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        disk_encryption = item['properties']['recommendations']['diskEncryption']
        if disk_encryption != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "disk_encryption_is_set_to_on",
                "negative_name": "disk_encryption_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def network_security_groups_is_set_to_on_2_7(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        nsgs = item['properties']['recommendations']['nsgs']
        if nsgs != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "network_security_groups_is_set_to_on",
                "negative_name": "network_security_groups_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def web_application_firewall_is_set_to_on_2_8(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        waf = item['properties']['recommendations']['waf']
        if waf != "On":
            items_flagged_list.append((resource_group))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "web_application_firewall_is_set_to_on",
                "negative_name": "web_application_firewall_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def next_generation_firewall_is_set_to_on_2_9(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        ngfw = item['properties']['recommendations']['ngfw']
        if ngfw != "On":
            items_flagged_list.append((resource_group))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "automatic_provisioning_of_monitoring_agent_is_set_to_on",
                "negative_name": "automatic_provisioning_of_monitoring_agent_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def vulnerability_assessment_is_set_to_on_2_10(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        vulnerability_assessment = item['properties']['recommendations']['vulnerabilityAssessment']
        if vulnerability_assessment != "On":
            items_flagged_list.append((resource_group))
            
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "automatic_provisioning_of_monitoring_agent_is_set_to_on",
                "negative_name": "automatic_provisioning_of_monitoring_agent_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def storage_encryption_is_set_to_on_2_11(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        storage_encryption = item['properties']['recommendations']['storageEncryption']
        if storage_encryption != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "storage_encryption_is_set_to_on",
                "negative_name": "storage_encryption_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def just_in_time_access_is_set_to_on_2_12(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        jit = item['properties']['recommendations']['jitNetworkAccess']
        if jit != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "just_in_time_access_is_set_to_on",
                "negative_name": "just_in_time_access_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def adaptive_application_controls_is_set_to_on_2_13(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        security_configurations = item['properties']['recommendations']['appWhitelisting']
        if security_configurations != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "adaptive_application_controls_is_set_to_on",
                "negative_name": "adaptive_application_controls_noto_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def sql_auditing_and_threat_detection_is_set_to_on_2_14(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        sqlAuditing = item['properties']['recommendations']['sqlAuditing']
        if sqlAuditing != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "sql_auditing_and_threat_detection_is_set_to_on",
                "negative_name": "sql_auditing_and_threat_detection_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def sql_encryption_is_set_to_on_2_15(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        sql_tde = item['properties']['recommendations']['sqlTde']
        if sql_tde != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "sql_encryption_is_set_to_on",
                "negative_name": "sql_encryption_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def security_contact_emails_is_set_2_16(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        emails = item['properties']['securityContactConfiguration']['securityContactEmails']
        if not emails:
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "security_contact_emails_is_set",
                "negative_name": "security_contact_emails_not_set",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def security_contact_phone_number_is_set_2_17(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        phone = item['properties']['securityContactConfiguration']['securityContactPhone']
        if not phone:
            items_flagged_list.append((resource_group))
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "security_contact_phone_number_is_set",
                "negative_name": "security_contact_phone_number_not_set",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def send_me_emails_about_alerts_is_set_to_on_2_18(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        notifications = item['properties']['securityContactConfiguration']['areNotificationsOn']
        if notifications != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "send_email_alerts_about_alerts_is_set_to_on",
                "negative_name": "send_email_alerts_about_alerts_not_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}

def send_email_also_to_subscription_owners_is_set_to_on_2_19(security_center):
    items_flagged_list = []
    for item in security_center:
        resource_group = item['name']
        send_admin = item['properties']['securityContactConfiguration']['sendToAdminOn']
        if send_admin != "On":
            items_flagged_list.append((resource_group))

    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(security_center)}
    metadata = {"finding_name": "send_email_also_to_subscription_owners_is_set_to_on",
                "negative_name": "send_email_also_to_subscription_owners_is_set_to_on",
                "columns": ["Resource Group"]}
    
    return {"items": items_flagged_list, "stats": stats, "metadata": metadata}