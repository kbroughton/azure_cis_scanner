
import subprocess
import yaml

# usage:
# az login
# az account set --subscription <your subscription id>
# python activity_log_alerts.py

# This script is set to run in check mode first, only printing out the commands it would run.
# First set the values below the "__name__" == "__main__" line.
# Then change check=True to check=False.


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
log_alert_policies = yaml.load(log_alert_policies_str)


def audit_log_alert_is_configured_rem(log_alert_policies, resource_group_name, default_action_group_name, subscription_id, check=False):
    for log_alert_policy in log_alert_policies[0:2]:
        category = log_alert_policy.get('category', 'Administrative')
        action_group_name = log_alert_policy.get('action_group_name', default_action_group_name)
        activity_log_alert_name = log_alert_policy['alert_name']
        operation_name = log_alert_policy['operation_name']
        
        command = 'az monitor activity-log alert create --debug -n {activity_log_alert_name} -g {resource_group_name}, --condition category={category} and operationName={operation_name} -a {action_group_name}'.format(
                activity_log_alert_name=activity_log_alert_name, resource_group_name=resource_group_name, category=category, action_group_name=action_group_name, operation_name=operation_name)
        if check:
        	print(command)
        else:
            try:
                response = subprocess.check_output(command)
            except Error as e:
                print(response)
                print(e)

if __name__ == "__main__":
	subscription_id = '<your subscription id>'
	resource_group_name = "Default-ActivityLogAlerts"
	action_group_name = '<your-action-group-here>'
	action_group_id = '/subscriptions/{sub_id}/resourceGroups/{resource_group_name}/providers/microsoft.insights/actionGroups/{action_group}'.format(
	                sub_id=subscription_id, resource_group_name=resource_group_name, action_group=action_group_name)
	audit_log_alert_is_configured_rem(log_alert_policies, resource_group_name, action_group_name, subscription_id, check=True)
