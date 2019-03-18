import json
import os
import yaml

from azure.mgmt.sql import SqlManagementClient
from azure_cis_scanner import utils

credentials = config['cli_credentials']
sp_credentials = config['sp_credentials']
subscription_id=config['subscription_id']

filtered_sql_servers_path = os.path.join(config['filtered_data_dir'], 'sql_servers_filtered.json')
sql_servers_path = os.path.join(config['raw_data_dir'], 'sql_databases.json')
sql_databases_path = os.path.join(config['raw_data_dir'], 'sql_servers.json')
sql_server_policies_path = os.path.join(config['raw_data_dir'], 'sql_server_policies.json')

import os
import yaml

def get_data():
    sql_servers = get_sql_servers(sql_servers_path)
    sql_databases = get_sql_databases(sql_databases_path, sql_servers)
    get_sql_server_policies(sql_server_policies_path, sql_servers)

def get_sql_servers(sql_servers_path) :
    sql_servers = json.loads(utils.call("az sql server list"))
    with open(sql_servers_path, 'w') as f:
        json.dump(sql_servers, f, indent=4, sort_keys=True)
    return sql_servers

def get_sql_databases(sql_databases_path, sql_servers) :
    sql_dbs = []
    for sql_server in sql_servers:
        server_name = sql_server['name']
        resource_group = sql_server['resourceGroup']
        dbs = json.loads(utils.call("az sql db list --resource-group {} --server {}".format(resource_group, server_name)))
        sql_dbs.extend(dbs)
    with open(sql_databases_path, 'w') as f:
        json.dump(sql_dbs, f, indent=4, sort_keys=True)
    return sql_dbs

def get_sql_server_policies(sql_server_policies_path, sql_servers):
    results = {}
    for sql_server in sql_servers:
        server_name = sql_server['name']
        resource_group = sql_server['resourceGroup']
        sql_server_policies = {}
        sql_server_policies['audit_policy'] = get_sql_server_audit_policies(subscription_id, resource_group, server_name)
        sql_server_policies['threat_detection_policy'] = get_sql_server_threat_detection_policies(subscription_id, resource_group, server_name)
        sql_server_policies['active_directory_admin_configurations'] = get_sql_server_active_directory_admin_configuration(subscription_id, resource_group, server_name)
        results[(resource_group, server_name)] = sql_server_policies
    with open(sql_server_policies_path, 'w') as f:
        yaml.dump(results, f)
    return results

def load_sql_servers(sql_servers_path):
    with open(sql_servers_path, 'r') as f:
        sql_servers = yaml.load(f, Loader=yaml.Loader)
    return sql_servers

def load_sql_server_policies(sql_server_policies_path):
    with open(sql_server_policies_path, 'r') as f:
        sql_server_policies = yaml.load(f, Loader=yaml.Loader)
    return sql_server_policies
    
# This function will be recentered around Azure Command Line, after such an option becomes available.
def get_sql_server_audit_policies(subscription_id, resource_group, server_name):
    endpoint = "https://management.azure.com/subscriptions/"+subscription_id+"/resourceGroups/"+resource_group+"/providers/Microsoft.Sql/servers/"+server_name+"/auditingSettings/Default?api-version=2015-05-01-preview"
    sql_server_audit_policy = utils.make_request(endpoint)
    sql_server_audit_policy = utils.jsonify(sql_server_audit_policy)
    return sql_server_audit_policy

# This function will be recentered around Azure Command Line, after such an option becomes available.
def get_sql_server_threat_detection_policies(subscription_id, resource_group, server_name):
    endpoint = "https://management.azure.com/subscriptions/"+subscription_id+"/resourceGroups/"+resource_group+"/providers/Microsoft.Sql/servers/"+server_name+"/securityAlertPolicies/Default?api-version=2015-05-01-preview"
    sql_server_threat_detection_policy = utils.make_request(endpoint)
    sql_server_threat_detection_policy = utils.jsonify(sql_server_threat_detection_policy)
    return sql_server_threat_detection_policy

def get_sql_server_active_directory_admin_configuration(subscription_id, resource_group, server_name):
    active_directory_admin_configuration = utils.call("az sql server ad-admin list --resource-group " + resource_group + " --server " + server_name)
    active_directory_admin_configuration = utils.jsonify(active_directory_admin_configuration)
    return active_directory_admin_configuration

##################
# Tests
##################
def wrap(pre, post):
    def decorate(func):
        def call(*args, **kwargs):
            pre(func, *args, **kwargs)
            result = func(*args, **kwargs)
            post(func, result, results, *args, **kwargs)
            return result
        return call
    return decorate

def remove_section_digits(name):
    filtered = []
    name_words = name.split('_')
    # remove trailing digits, taking care not to remove 90 in ...than_90_days_4_1_7
    for i, word in enumerate(name_words):
        if not word.isdigit() or ( (i < len(name_words)-2) and not name_words[i+1].isdigit()):
            filtered.append(word)
    return '_'.join(filtered)

def trace_in(func, *args, **kwargs):
    pass

def trace_out(func, result, *args, **kwargs):
    name = remove_section_digits(func.__name__)
    finding_results = results.get(name, {})
    if finding_results:
        items_flagged_list = finding_results["items"]
        items_checked = finding_results["stats"]["items_checked"]
    else:
        items_flagged_list = []
        items_checked = 0
    items_checked += 1
    if not result:
        items_flagged_list.append((kwargs['resource_group'], kwargs['server_name']))
           
    results[name] = {"items": items_flagged_list, "stats": {"items_checked": items_checked}}
        
results = {}

def test_controls() :
    global results
    sql_servers = load_sql_servers(sql_servers_path)
    sql_server_policies = load_sql_server_policies(sql_server_policies_path)
    
    for (resource_group, server_name), sql_server_policy in sql_server_policies.items():
        sql_server_audit_policy = sql_server_policies[(resource_group, server_name)]['audit_policy']
        sql_server_threat_detection_policy = sql_server_policies[(resource_group, server_name)]['threat_detection_policy']
        sql_server_active_directory_admin_configurations = sql_server_policies[(resource_group, server_name)]['active_directory_admin_configurations']

        auditing_is_set_to_on_4_1_1(sql_server_audit_policy, resource_group=resource_group, server_name=server_name)
        threat_detection_is_set_to_on_4_1_2(sql_server_threat_detection_policy, resource_group=resource_group, server_name=server_name)
        threat_detection_types_is_set_to_all_4_1_3(sql_server_threat_detection_policy, resource_group=resource_group, server_name=server_name)
        send_alerts_to_is_set_4_1_4(sql_server_threat_detection_policy, resource_group=resource_group, server_name=server_name)
        email_service_and_co_administrators_is_enabled_4_1_5(sql_server_threat_detection_policy, resource_group=resource_group, server_name=server_name)
        auditing_retention_is_greater_than_90_days_4_1_6(sql_server_audit_policy, resource_group=resource_group, server_name=server_name)
        threat_detection_retention_is_greater_than_90_days_4_1_7(sql_server_threat_detection_policy, resource_group=resource_group, server_name=server_name)
        azure_active_directory_admin_is_configured_4_1_8(sql_server_active_directory_admin_configurations, resource_group=resource_group, server_name=server_name)

    stats_results = {}
    for finding in results:
        items_flagged_list = results[finding]["items"]
        items_checked = results[finding]["stats"]["items_checked"]
        items_flagged = len(items_flagged_list)
        stats = {'items_flagged': len(items_flagged_list),
                 'items_checked': items_checked}
        metadata = {"finding_name": finding,
                    "negative_name": "",
                    "columns": ["Region", "Server"]}            
        stats_results[finding] = {"items": items_flagged_list, "stats": stats, "metadata": metadata}
        
    with open(filtered_sql_servers_path, 'w') as f:
        yaml.dump(stats_results, f)
    # clear results for next run
    results = {}
    return stats_results

@wrap(trace_in, trace_out)
def auditing_is_set_to_on_4_1_1(sql_server_audit_policies, resource_group=None, server_name=None):
    if sql_server_audit_policies["properties"]["state"] == "Disabled" :
        return False
    else:
        return True

@wrap(trace_in, trace_out)
def threat_detection_is_set_to_on_4_1_2(sql_server_threat_detection_policies, resource_group=None, server_name=None):
    if sql_server_threat_detection_policies["properties"]["state"] == "Disabled" :
        return False
    else:
        return True
    
@wrap(trace_in, trace_out)
def threat_detection_types_is_set_to_all_4_1_3(sql_server_threat_detection_policies, resource_group=None, server_name=None):
    if sql_server_threat_detection_policies["properties"]["state"] == "Disabled" or sql_server_threat_detection_policies["properties"]["disabledAlerts"] != "":
        return False
    else:
        return True

@wrap(trace_in, trace_out)
def send_alerts_to_is_set_4_1_4(sql_server_threat_detection_policies, resource_group=None, server_name=None):
    if sql_server_threat_detection_policies["properties"]["state"] == "Disabled" or sql_server_threat_detection_policies["properties"]["emailAddresses"] == "":
        return False
    else:
        return True

@wrap(trace_in, trace_out)
def email_service_and_co_administrators_is_enabled_4_1_5(sql_server_threat_detection_policies, resource_group=None, server_name=None):
    if sql_server_threat_detection_policies["properties"]["emailAccountAdmins"] == "Disabled":
        return False
    else:
        return True

@wrap(trace_in, trace_out)
def auditing_retention_is_greater_than_90_days_4_1_6(sql_server_audit_policies, resource_group=None, server_name=None):
    if (sql_server_audit_policies["properties"]["state"] == "Disabled"):
        return False
    retention_days = int(sql_server_audit_policies["properties"]["retentionDays"])
    if (retention_days == 0 ) or (retention_days > 90):
        return True
    else:    
        return False
    
@wrap(trace_in, trace_out)
def threat_detection_retention_is_greater_than_90_days_4_1_7(sql_server_threat_detection_policies, resource_group=None, server_name=None):
    if (sql_server_threat_detection_policies["properties"]["state"] == "Disabled"):
        return False
    retention_days = int(sql_server_threat_detection_policies["properties"]["retentionDays"])
    if (retention_days) ==0 or (retention_days > 90):
        return True
    else:    
        return False
    
@wrap(trace_in, trace_out)
def azure_active_directory_admin_is_configured_4_1_8(sql_server_active_directory_admin_configurations, resource_group=None, server_name=None):
    if not sql_server_active_directory_admin_configurations:
        return False
    else:
        return True