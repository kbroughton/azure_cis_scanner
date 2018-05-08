# Generate files in azcli_out

monitor_diagnostic_settings_path = os.path.join(raw_data_dir, 'monitor_diagnostic_settings.json')


def get_monitor_diagnostic_settings(monitor_diagnostic_settings_path, resource_ids):
    """
    @monitor_diagnostic_settings_path: string - path to output json file
    @returns: list of activity_log_alerts dicts
    """
    monitor_diagnostic_settings_results = {}
    for resource_id in resource_ids:
        monitor_diagnostic_settings = !az monitor diagnostic-settings list --resource {resource_id}
        monitor_diagnostic_settings = yaml.load(monitor_diagnostic_settings.nlstr)
        monitor_diagnostic_settings_results[resource_id] = monitor_diagnostic_settings
    with open(monitor_diagnostic_settings_path, 'w') as f:
        yaml.dump(monitor_diagnostic_settings_results, f)
    return monitor_diagnostic_settings_results

def load_monitor_diagnostic_settings(monitor_diagnostic_settings):
    with open(monitor_diagnostic_settings, 'r') as f:
        monitor_diagnostic_settings = yaml.load(f)
    return monitor_diagnostic_settings

monitor_log_profiles_path = os.path.join(raw_data_dir, 'monitor_log_profiles.json')

def get_monitor_log_profiles(monitor_log_profiles_path):
    monitor_log_profiles = !az monitor log-profiles list
    monitor_log_profiles = yaml.load(monitor_log_profiles.nlstr)
    with open(monitor_log_profiles_path, 'w') as f:
        yaml.dump(monitor_log_profiles, f)
    return monitor_log_profiles

def load_monitor_log_profiles(monitor_log_profiles_path):
    with open(monitor_log_profiles_path, 'r') as f:
        monitor_log_profiles = yaml.load(f)
    return monitor_log_profiles

activity_logs_path = os.path.join(raw_data_dir, 'activity_logs.json')

activity_log_starttime_timedelta = datetime.timedelta(days=90)
def get_start_time(timedelta=datetime.timedelta(days=90)):
    """
    Given datetime.timedelta(days=days, hours=hours), return string in iso tz format 
    """
    return datetime.datetime.strftime(datetime.datetime.now() - timedelta, "%Y-%m-%dT%H:%M:%SZ")

def get_activity_logs(activity_log_path, resource_groups):
    activity_logs = {}
    start_time = get_start_time(activity_log_starttime_timedelta)
    for resource_group in resource_groups:
        resource_group = resource_group['name']
        activity_log = !az monitor activity-log list --resource-group {resource_group} --start-time {start_time}
        activity_log = yaml.load(activity_log.nlstr)
        activity_logs[resource_group] = activity_log
    with open(activity_log_path, 'w') as f:
        yaml.dump(activity_logs, f)
    return activity_logs    

def load_activity_logs(activity_logs_path):
    with open(activity_logs_path, 'r') as f:
        activity_logs = yaml.load(f)
    return activity_logs

activity_log_alerts_path = os.path.join(raw_data_dir, 'activity_log_alerts.json')

def get_activity_log_alerts(activity_log_alerts_path, resource_groups):
    activity_log_alerts = !az monitor activity-log alert list
    activity_log_alerts = yaml.load(activity_log_alerts.nlstr)
    #     for resource_group in resource_groups:
    #         resource_group = resource_group['name']
    #         activity_log_alert = !az monitor activity-log alert list --resource-group {resource_group}
    #         activity_log_alert = yaml.load(activity_log_alert.nlstr)
    #         activity_log_alerts[resource_group] = activity_log_alert
    with open(activity_log_path, 'w') as f:
        yaml.dump(activity_log_alerts, f)
    return activity_log_alerts   

def load_activity_log_alerts(activity_log_alerts_path):
    with open(activity_log_alerts_path, 'r') as f:
        activity_log_alerts = yaml.load(f)
    return activity_log_alerts


##################
# Tests
##################

def a_log_profile_exists_5_1(monitor_log_profiles):
    if monitor_log_profiles:
        return True, [], ()
    else:
        return False, [], ()

def logging_monitoring_tests():
    """
    Use the data in azcli_out or in memory to run tests.
    Filtered output of azcli_out for failing systems is placed in azcli_out_filtered
    """
    
    results = {}
    return False

# Todo, untested as we have [] for log-profiles
#@gen_results(results)
def activity_log_retention_is_set_365_days_or_greater_5_2(monitor_log_profiles):
    if monitor_log_profiles:
        activity_log_retention_failed = []
        for profile in monitor_log_profiles:
            activity_log_retention_is_set = monitor_log_profiles['retentionPolicy']
            activity_log_retention_is_set = yaml.load(activity_log_retention_is_set.nlstr)
            if activity_log_retention_is_set >= MIN_ACTIVITY_LOG_RETENDION_DAYS:
                activity_log_retention_failed.append(profile)
        if activity_log_retention_failed:
            return False, activity_log_retention, ()
        else:
            return True, [], ()
    else:
        return False, [], ()
    
# 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12
def activity_log_alert_is_configured(activity_log_alerts, resource_groups):
    """
    #TODO WIP
    For each resource_group determine if activity-log alerts are configured correctly
    @returns: list of [resource_group, True of False for 5.3 to 5.12 in succession]
    """
    activity_log_alert_is_configured_fails = []

    create_policy_assignment_failed = True
    create_or_update_network_security_group_failed = True
    delete_network_security_group_failed_failed = True
    create_or_update_network_security_group_rule_failed = True
    delete_network_security_group_rule_failed = True
    create_or_update_security_solution_failed = True
    delete_security_solution_failed = True
    update_or_create_SQL_server_firewall_rule_failed = True
    delete_SQL_server_firewall_rule_failed = True
    update_security_policy_failed = True
    for resource_group, log_alerts in activity_log_alerts.items():
        activity_log_alert_results = [True]*10
        for log_alert in log_alerts:
            print("LOGALERT", log_alert)
            condition = log_alert.get('condition', [])
            if not condition:
                continue
            conditions = condition.get('allOf', [])
            print("CONDITIONS", conditions)
            if not conditions:
                continue
            for condition in conditions:
                print(condition)
                if "Microsoft.Authorization/policyAssignments/write" in condition['additionalProperties'].values():
                    create_policy_assignment_failed = False
                if "Microsoft.Network/networkSecurityGroups/write" in condition['additionalProperties'].values():
                    create_or_update_network_security_group_failed = False
                if "Microsoft.Network/networkSecurityGroups/delete" in condition['additionalProperties'].values():
                    delete_network_security_group_failed = False
                if "Microsoft.Network/networkSecurityGroups/securityRules/write" in condition['additionalProperties'].values():
                    create_or_update_network_security_group_rule_failed = False
                if "Microsoft.Network/networkSecurityGroups/securityRules/delete" in condition['additionalProperties'].values():
                    delete_network_security_group_rule_failed = False
                if "Microsoft.Security/securitySolutions/write" in condition['additionalProperties'].values():
                    create_or_update_security_solution_failed = False
                if "Microsoft.Security/securitySolutions/delete" in condition['additionalProperties'].values():
                    delete_security_solution_failed = False
                if "Microsoft.Sql/servers/firewallRules/write" in condition['additionalProperties'].values():
                    update_or_create_SQL_server_firewall_rule_failed = False
                if "Microsoft.Sql/servers/firewallRules/delete" in condition['additionalProperties'].values():
                    delete_SQL_server_firewall_rule_failed = False
                if "Microsoft.Security/policies/write" in condition['additionalProperties'].values():
                    update_security_policy_failed = False
            activity_log_alert_results = [create_policy_assignment_failed,
                                      create_or_update_network_security_group_failed,
                                      delete_network_security_group_failed_failed,
                                      create_or_update_network_security_group_rule_failed,
                                      delete_network_security_group_rule_failed,
                                      create_or_update_security_solution_failed,
                                      delete_security_solution_failed,
                                      update_or_create_SQL_server_firewall_rule_failed,
                                      delete_SQL_server_firewall_rule_failed,
                                      update_security_policy_failed]
            if not (create_policy_assignment_failed and 
                    create_or_update_network_security_group_failed and 
                    delete_network_security_group_failed_failed and create_or_update_network_security_group_rule_failed and delete_network_security_group_rule_failed and create_or_update_security_solution_failed and delete_security_solution_failed and update_or_create_SQL_server_firewall_rule_failed and delete_SQL_server_firewall_rule_failed and update_security_policy_failed):
                activity_log_alert_is_configured_fails.append([resource_group] + activity_log_alert_results)
    return activity_log_alert_is_configured_fails
    
    
resource_ids_for_diagnostic_settings_path = os.path.join(raw_data_dir, 'resource_ids_for_diagnostic_settings.json')

def get_resource_ids_for_diagnostic_settings():
    resource_ids = []
    # Other resource_ids could be gathered.  So far, only keyvault
    keyvaults = !az keyvault list    
    keyvaults = yaml.load(keyvaults.nlstr)
    for keyvault in keyvaults:
        resource_ids.append(keyvault['id'])
    with open(resource_ids_for_diagnostic_settings_path, 'w') as f:
        yaml.dump(resource_ids, f)
    return resource_ids

def load_resource_ids_for_diagnostic_settings(resource_ids_for_diagnostic_settings_path):
    with open(resource_ids_for_diagnostic_settings_path, 'r') as f:
        resource_ids_for_diagnostic_settings = yaml.load(f)
    return resource_ids_for_diagnostic_settings
    
#@gen_results(results)
MIN_ACTIVITY_LOG_RETENDION_DAYS = 365
MIN_KEY_VAULT_RETENTION_DAYS = 180
def logging_for_azure_keyvault_is_enabled_13(resource_ids_for_diagnostic_settings):        
    items_flagged_list = []
    for resource_id in resource_ids_for_diagnostic_settings:
        keyvault_settings = !az monitor diagnostic-settings list --resource {resource_id}
        keyvault_settings = yaml.load(keyvault_settings.nlstr)
        *prefix, resource_group, _, _, _, keyvault_name = resource_id.split('/')
        if keyvault_settings['value']:
            enabled = keyvault_settings['logs']['enabled']
            retention_enabled = keyvault_settings['logs']['retentionPolicy']['enabled']
            retention_days = keyvault_settings['logs']['retentionPolicy']['days']
            if not (enabled and retention_enabled and (retention_days >= MIN_KEY_VAULT_RETENTION_DAYS)):
                items_flagged_list.append((keyvault_name, enabled, retention_enabled, retention_days))
        else:
            items_flagged_list.append((resource_group, keyvault_name, "False", "False", "None"))
            
    stats = {"items_flagged": len(items_flagged_list), "items_checked": len(resource_ids)}
    if items_flagged_list:
        return False, items_flagged_list
    else:
        return True, []
              
    