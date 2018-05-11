# Generate files in azcli_out
import utils

sql_servers = []
sql_server_audit_policies = {}
sql_server_threat_detection_policies = {}
sql_server_active_directory_admin_configurations = {}
results = []

def get_data() :
    get_sql_servers()
    # sql_servers_active_directory_admin_configurations = get_sql_server_active_directory_admin_configuration(sql_servers)
    # sql_server_audit_policies = get_sql_server_audit_policies(sql_servers)
    sql_server_threat_detection_policies = get_sql_server_threat_detection_policies()

def get_sql_servers() :
    sql_servers_string = utils.call("az sql server list")
    sql_servers_json = utils.jsonify(sql_servers_string)
    for sql_server in sql_servers_json :
        sql_servers.append(sql_server)
    return sql_servers_json

# This function will be recentered around Azure Command Line, after such an option becomes available.
def get_sql_server_audit_policies() :
    subscriptionId = utils.get_subscription_id()
    for sql_server in sql_servers :
        resource_group = sql_server["resourceGroup"]
        server_name = sql_server["name"]
        endpoint = "https://management.azure.com/subscriptions/"+subscriptionId+"/resourceGroups/"+resource_group+"/providers/Microsoft.Sql/servers/"+server_name+"/auditingSettings/Default?api-version=2015-05-01-preview"
        sql_server_audit_policy = utils.make_request(endpoint)
        sql_server_audit_policy = utils.jsonify(sql_server_audit_policy)
        sql_server_audit_policies[utils.stringify(sql_server)] = sql_server_audit_policy
    return sql_server_audit_policies

# This function will be recentered around Azure Command Line, after such an option becomes available.
def get_sql_server_threat_detection_policies() :
    subscriptionId = utils.get_subscription_id()
    for sql_server in sql_servers :
        resource_group = sql_server["resourceGroup"]
        server_name = sql_server["name"]
        endpoint = "https://management.azure.com/subscriptions/"+subscriptionId+"/resourceGroups/"+resource_group+"/providers/Microsoft.Sql/servers/"+server_name+"/securityAlertPolicies/Default?api-version=2015-05-01-preview"
        sql_server_threat_detection_policy = utils.make_request(endpoint)
        sql_server_threat_detection_policy = utils.jsonify(sql_server_threat_detection_policy)
        sql_server_threat_detection_policies[utils.stringify(sql_server)] = sql_server_threat_detection_policy
    return sql_server_threat_detection_policies

def get_sql_server_active_directory_admin_configuration():
    for sql_server in sql_servers:
        active_directory_admin_configuration = utils.call("az sql server ad-admin list --resource-group " + sql_server['resourceGroup'] + " --server " + sql_server['name'])
        active_directory_admin_configuration = utils.jsonify(active_directory_admin_configuration)
        sql_server_active_directory_admin_configurations[utils.stringify(sql_server)] = active_directory_admin_configuration
    return sql_server_active_directory_admin_configurations

##################
# Tests
##################

def run_tests() :
    get_data()
    results.append(ensure_azure_active_directory_admin_is_configured_for_sql_server_4_1_8())
    results.append(auditing_for_sql_servers_is_on_4_1_1())
    results.append(ensure_that_threat_detection_for_sql_servers_is_on_4_1_2())
    results.append(ensure_that_threat_detection_types_is_set_to_all_4_1_3())
    results.append(ensure_that_send_alerts_to_is_set_4_1_4())
    results.append(ensure_that_email_service_and_coadministrators_is_enabled_4_1_5())
    results.append(ensure_that_auditing_retention_is_greater_than_90_days_4_1_6())
    results.append(ensure_that_threat_detection_retention_is_greater_than_90_days_4_1_7())
    results.append(ensure_azure_active_directory_admin_is_configured_for_sql_server_4_1_8())

def auditing_for_sql_servers_is_on_4_1_1():
    i = 0
    flagged_items = []
    for audit_policy in sql_server_audit_policies.values() :
        if audit_policy["properties"]["state"] == "Disabled" :
            flagged_items.append(list(sql_server_audit_policies.keys()[i]))
        i += 1
    return flagged_items


def ensure_that_threat_detection_for_sql_servers_is_on_4_1_2():
    i = 0
    flagged_items = []
    for threat_detection_policy in sql_server_threat_detection_policies.values():
        if threat_detection_policy["properties"]["state"] == "Disabled" :
            flagged_items.append(list(threat_detection_policy.keys())[i])
        i += 1
    return flagged_items

def ensure_that_threat_detection_types_is_set_to_all_4_1_3():
    i = 0
    flagged_items = []
    for threat_detection_policy in sql_server_threat_detection_policies.values():
        if threat_detection_policy["properties"]["state"] == "Disabled" or threat_detection_policy["properties"]["disabledAlerts"] != "":
            flagged_items.append(list(threat_detection_policy.keys())[i])
        i += 1
    return flagged_items

def ensure_that_send_alerts_to_is_set_4_1_4():
    i = 0
    flagged_items = []
    for threat_detection_policy in sql_server_threat_detection_policies.values():
        if threat_detection_policy["properties"]["state"] == "Disabled" or threat_detection_policy["properties"]["emailAddresses"] != "":
            flagged_items.append(list(threat_detection_policy.keys())[i])
        i += 1
    return flagged_items

def ensure_that_email_service_and_coadministrators_is_enabled_4_1_5():
    i = 0
    flagged_items = []
    for threat_detection_policy in sql_server_threat_detection_policies.values():
        if threat_detection_policy["properties"]["state"] == "Disabled" or threat_detection_policy["properties"]["emailAccountAdmins"] != "":
            flagged_items.append(list(threat_detection_policy.keys())[i])
        i += 1
    return flagged_items

def ensure_that_auditing_retention_is_greater_than_90_days_4_1_6():
    i = 0
    flagged_items = []
    for audit_policy in sql_server_audit_policies.values() :
        if audit_policy["properties"]["state"] == "Disabled" or int(audit_policy["properties"]["retentionDays"]) > 90 :
            flagged_items.append(list(sql_server_audit_policies.keys()[i]))
        i += 1
    return flagged_items

def ensure_that_threat_detection_retention_is_greater_than_90_days_4_1_7():
    i = 0
    flagged_items = []
    for threat_detection_policy in sql_server_threat_detection_policies.values():
        if threat_detection_policy["properties"]["state"] == "Disabled" or int(threat_detection_policy["properties"]["retentionDays"]) > 90:
            flagged_items.append(list(threat_detection_policy.keys())[i])
        i += 1
    return flagged_items

def ensure_azure_active_directory_admin_is_configured_for_sql_server_4_1_8():
    i = 0              # using index because there is not one-to-one mapping of key-value pairs.
    flagged_items = []
    for sql_server_admin_configuration in sql_server_active_directory_admin_configurations.values() :
        if not sql_server_admin_configuration :
            flagged_items.append(list(sql_server_active_directory_admin_configurations.keys())[i])
        i += 1
    return flagged_items
