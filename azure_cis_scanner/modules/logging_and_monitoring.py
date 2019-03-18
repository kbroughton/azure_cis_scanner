#%load {scanner_dir}/scanner/modules/logging_and_monitoring.py

# Generate files in raw_data_dir

import datetime
import json
import os
import traceback
import yaml

from azure.mgmt.monitor import MonitorManagementClient
from azure_cis_scanner import utils

from azure_cis_scanner.utils import get_list_from_paged_results, get_service_principal_credentials, AzScannerException

monitor_diagnostic_settings_path = os.path.join(config['raw_data_dir'], 'monitor_diagnostic_settings.json')
monitor_log_profiles_path = os.path.join(config['raw_data_dir'], 'monitor_log_profiles.json')
activity_logs_path = os.path.join(config['raw_data_dir'], 'activity_logs.json')
activity_log_alerts_path = os.path.join(config['raw_data_dir'], 'activity_log_alerts.json')
resource_groups_path = os.path.join(config['raw_data_dir'], "resource_groups.json")
resource_ids_for_diagnostic_settings_path = os.path.join(config['raw_data_dir'], 'resource_ids_for_diagnostic_settings.json')
resource_diagnostic_settings_path = os.path.join(config['raw_data_dir'], 'resource_diagnostic_settings.json')
logging_and_monitoring_filtered_path = os.path.join(config['filtered_data_dir'], 'logging_and_monitoring_filtered.json')
credentials = config['cli_credentials']
subscription_id = config['subscription_id']

def get_resource_ids_for_diagnostic_settings():
    resource_ids = []
    # Other resource_ids could be gathered.  So far, only keyvault
    keyvaults = json.loads(utils.call("az keyvault list"))
    for keyvault in keyvaults:
        resource_ids.append(keyvault['id'])
    with open(resource_ids_for_diagnostic_settings_path, 'w') as f:
        json.dump(resource_ids, f, indent=4, sort_keys=True)
    return resource_ids

def load_resource_ids_for_diagnostic_settings(resource_ids_for_diagnostic_settings_path):
    with open(resource_ids_for_diagnostic_settings_path, 'r') as f:
        resource_ids_for_diagnostic_settings = yaml.load(f, Loader=yaml.Loader)
    return resource_ids_for_diagnostic_settings

def get_resource_diagnostic_settings(resource_ids_for_diagnostic_settings):
    keyvault_settings_list = []
    for resource_id in resource_ids_for_diagnostic_settings:
        keyvault_settings = json.loads(utils.call("az monitor diagnostic-settings list --resource {resource_id}".format(resource_id=resource_id)))
        *prefix, resource_group, _, _, _, keyvault_name = resource_id.split('/')
        if not keyvault_settings['value']:
            keyvault_settings['value'].append({'keyvault_name': keyvault_name, 'resourceGroup': resource_group})
        else:
            for setting in keyvault_settings['value']:
                setting['keyvault_name'] = keyvault_name
        print(keyvault_settings)
        keyvault_settings_list.append(keyvault_settings)
        
    with open(resource_diagnostic_settings_path, 'w') as f:
        yaml.dump(keyvault_settings_list, f)
    return resource_ids_for_diagnostic_settings 

def load_resource_diagnostic_settings(resource_diagnostic_settings_path):
    with open(resource_diagnostic_settings_path, 'r') as f:
        resource_diagnostic_settings = yaml.load(f, Loader=yaml.Loader)
    return resource_diagnostic_settings        
        
def get_monitor_diagnostic_settings(monitor_diagnostic_settings_path, resource_ids):
    """
    @monitor_diagnostic_settings_path: string - path to output json file
    @returns: list of activity_log_alerts dicts
    """
    monitor_diagnostic_settings_results = {}
    for resource_id in resource_ids:
        monitor_diagnostic_settings = json.loads(utils.call("az monitor diagnostic-settings list --resource {resource_id}".format(resource_id=resource_id)))
        monitor_diagnostic_settings_results[resource_id] = monitor_diagnostic_settings
    with open(monitor_diagnostic_settings_path, 'w') as f:
        json.dump(monitor_diagnostic_settings_results, f, indent=4, sort_keys=True)
    return monitor_diagnostic_settings_results

def load_monitor_diagnostic_settings(monitor_diagnostic_settings_path):
    with open(monitor_diagnostic_settings_path, 'r') as f:
        monitor_diagnostic_settings = yaml.load(f, Loader=yaml.Loader)
    return monitor_diagnostic_settings


def get_monitor_log_profiles(monitor_log_profiles_path):
    monitor_log_profiles = json.loads(utils.call("az monitor log-profiles list"))
    with open(monitor_log_profiles_path, 'w') as f:
        json.dump(monitor_log_profiles, f, indent=4, sort_keys=True)
    return monitor_log_profiles

def load_monitor_log_profiles(monitor_log_profiles_path):
    with open(monitor_log_profiles_path, 'r') as f:
        monitor_log_profiles = yaml.load(f, Loader=yaml.Loader)
    return monitor_log_profiles

# duplicated in storage_accounts.log
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
        activity_log = json.loads(utils.call("az monitor activity-log list --resource-group {resource_group} --start-time {start_time}".format(
            resource_group=resource_group, start_time=start_time)))
        activity_logs[resource_group] = activity_log
    with open(activity_logs_path, 'w') as f:
        json.dump(activity_logs, f, indent=4, sort_keys=True)
    return activity_logs    

def load_activity_logs(activity_logs_path):
    with open(activity_logs_path, 'r') as f:
        activity_log = yaml.load(f, Loader=yaml.Loader)
    return activity_log

def get_activity_log_alerts(activity_log_alerts_path):
    activity_log_alerts = json.loads(utils.call("az monitor activity-log alert list"))
    with open(activity_log_alerts_path, 'w') as f:
        json.dump(activity_log_alerts, f, indent=4, sort_keys=True)
    return activity_log_alerts   

def load_activity_log_alerts(activity_log_alerts_path):
    with open(activity_log_alerts_path, 'r') as f:
        activity_log_alerts = yaml.load(f, Loader=yaml.Loader)
    return activity_log_alerts

def get_data():
    resource_ids_for_diagnostic_settings = get_resource_ids_for_diagnostic_settings()
    resource_groups = utils.load_resource_groups(resource_groups_path)
    get_monitor_log_profiles(monitor_log_profiles_path)
    get_monitor_diagnostic_settings(monitor_diagnostic_settings_path, resource_ids_for_diagnostic_settings)
    get_activity_log_alerts(activity_log_alerts_path)
    get_activity_logs(activity_logs_path, resource_groups)
    get_resource_diagnostic_settings(resource_ids_for_diagnostic_settings)

    
    
##################
# Tests
##################

def test_controls():
    """
    Use the data in raw_data_dir or in memory to run tests.
    Filtered output of raw_data_dir for failing systems is placed in filtered_data_dir
    """
    resource_ids_for_diagnostic_settings = load_resource_ids_for_diagnostic_settings(resource_ids_for_diagnostic_settings_path)
    resource_diagnostic_settings = load_resource_diagnostic_settings(resource_diagnostic_settings_path)
    resource_groups = utils.load_resource_groups(resource_groups_path)
    monitor_log_profiles = load_monitor_log_profiles(monitor_log_profiles_path)
    monitor_diagnostic_settings = load_monitor_diagnostic_settings(monitor_diagnostic_settings_path)
    activity_log_alerts = load_activity_log_alerts(activity_log_alerts_path)
    activity_logs = load_activity_logs(activity_logs_path)
    
    
    results = {}
    results['a_log_profile_exists'] = a_log_profile_exists_5_1(monitor_log_profiles)
    results['activity_log_retention_is_set_365_days_or_greater'] = activity_log_retention_is_set_365_days_or_greater_5_2(monitor_log_profiles)
    results['activity_log_alert_is_configured'] = activity_log_alert_is_configured(activity_log_alerts, log_alert_policies)
    results['logging_for_azure_keyvault_is_enabled'] = logging_for_azure_keyvault_is_enabled_5_13(resource_diagnostic_settings)

    with open(logging_and_monitoring_filtered_path, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)
    return results


def a_log_profile_exists_5_1(monitor_log_profiles):
    items_flagged_list = []
    if monitor_log_profiles:
        pass
    else:
        items_flagged_list.append(("No log profile"))
        
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': min(1, len(items_flagged_list))}
    metadata = {"finding_name": "a_log_profile_exists",
                "negative_name": "",
                "columns": ["Monitor Log Profile"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}
    

# Todo, untested as we have [] for log-profiles
#@gen_results(results)
def activity_log_retention_is_set_365_days_or_greater_5_2(monitor_log_profiles):
    items_flagged_list = []
    if monitor_log_profiles:
        for monitor_log_profile in monitor_log_profiles:
            days = monitor_log_profile.get('retentionPolicy', {}).get('days', -1)
            if monitor_log_profile.get('retentionPolicy') and (monitor_log_profile.get('retentionPolicy').get('days') == 0) and (monitor_log_profile.get('retentionPolicy').get('enabled') == False):
                # retention is forever
                continue
            if monitor_log_profile.get('retentionPolicy', {}).get('days') <= MIN_ACTIVITY_LOG_RETENDION_DAYS:
                items_flagged_list.append((monitor_log_profile['id'], monitor_log_profile['storageAccountId'], days))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(monitor_log_profiles) if monitor_log_profiles else 1}
    metadata = {"finding_name": "activity_log_retention_is_set_365_days_or_greater",
                "negative_name": "",
                "columns": ["Monitor Log Profile", "Retention Days"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}

# 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12    
log_alert_policies_str = '''
- alert_name: 'create_policy_assignment'
  operation_name: 'Microsoft.Authorization/policyAssignments/write'
  present: False
- alert_name: 'create_or_update_network_security_group'
  operation_name: 'Microsoft.Network/networkSecurityGroups/write'
  present: False
- alert_name: 'delete_network_security_group'
  operation_name: 'Microsoft.Network/networkSecurityGroups/delete'
  present: False
- alert_name: 'create_or_update_network_security_group_rule'
  operation_name: 'Microsoft.Network/networkSecurityGroups/securityRules/write'
  present: False
- alert_name: 'delete_network_security_group_rule'
  operation_name: 'Microsoft.Network/networkSecurityGroups/securityRules/delete'
  present: False
- alert_name: 'create_or_update_security_solution'
  operation_name: 'Microsoft.Security/securitySolutions/write'
  present: False
- alert_name: 'delete_security_solution'
  operation_name: 'Microsoft.Security/securitySolutions/delete'
  present: False
- alert_name: 'update_or_create_SQL_server_firewall_rule'
  operation_name: 'Microsoft.Sql/servers/firewallRules/write'
  present: False
- alert_name: 'delete_SQL_server_firewall_rule'
  operation_name: 'Microsoft.Sql/servers/firewallRules/delete'
  present: False
- alert_name: 'update_security_policy'
  operation_name: 'Microsoft.Security/policies/write'
  present: False
'''
log_alert_policies = yaml.load(log_alert_policies_str, Loader=yaml.Loader)

def activity_log_alert_is_configured(activity_log_alerts, log_alert_policies):
    """
    #TODO WIP
    For each resource_group determine if activity-log alerts are configured correctly
    @returns: list of [resource_group, True of False for 5.3 to 5.12 in succession]
    """
    items_flagged_list = []

  
    for log_alert in activity_log_alerts:
        condition = log_alert.get('condition', [])
        if not condition:
            continue
        conditions = condition.get('allOf', [])
        if not conditions:
            continue
        for condition in conditions:
            for log_alert_policy in log_alert_policies:
                if condition.get('equals') and (condition.get('equals') == log_alert_policy["operation_name"]):
                    log_alert_policy["present"] = True

    for log_alert_policy in log_alert_policies:
        if log_alert_policy['present'] == False:
            items_flagged_list.append((log_alert_policy['alert_name'], log_alert_policy['operation_name']))
    
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(log_alert_policies)}
    metadata = {"finding_name": "activity_log_alert_is_configured",
                "negative_name": "",
                "columns": ["Missing Policy"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}
                                                                    
#@gen_results(results)
MIN_ACTIVITY_LOG_RETENDION_DAYS = 365
MIN_KEY_VAULT_RETENTION_DAYS = 180
def logging_for_azure_keyvault_is_enabled_5_13(resource_diagnostic_settings):        
    items_flagged_list = []
    for setting in resource_diagnostic_settings:
        keyvault_settings_values = setting['value']
        if keyvault_settings_values:
            for value in keyvault_settings_values:
                # Do we need to loop over ['logs'] list as well?  My lists are length 1, only checking [0]
                keyvault_name = value['keyvault_name']
                resource_group = value['resourceGroup']
                if not value.get('logs', None):
                    enabled = False
                    retention_enabled = False
                    retention_days = 0
                else:
                    enabled = value['logs'][0]['enabled']
                    retention_enabled = value['logs'][0]['retentionPolicy']['enabled']
                    retention_days = value['logs'][0]['retentionPolicy']['days']                    
                if not (enabled and retention_enabled and (retention_days >= MIN_KEY_VAULT_RETENTION_DAYS)):
                    items_flagged_list.append((keyvault_name, enabled, retention_enabled, retention_days))
        else:
            items_flagged_list.append((resource_group, keyvault_name, "False", "False", "None"))
            
    stats = {'items_flagged': len(items_flagged_list),
             'items_checked': len(resource_diagnostic_settings)}
    metadata = {"finding_name": "logging_for_azure_keyvault_is_enabled",
                "negative_name": "",
                "columns": ["Keyvault", "Enabled", "Retention Enabled", "Retention Days"]}            
    return  {"items": items_flagged_list, "stats": stats, "metadata": metadata}
              
