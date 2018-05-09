
# Could convert these to subprocess
# Alternatively and much simpler, convert it to a bash script with some error handling, piping results to output.

# Looks like there might only be a few distinct calls.  All these are filters on data that come from the same endpoint and we should only make a single call for the raw data. 
# '.properties.recommendations.nsgs'
# '.properties.recommendations.waf'
# '.properties.recommendations.vulnerabilityAsses
# '.properties.recommendations.ngfw'

# Then write python tests for each finding.

automatic_provisioning_of_monitoring_agent = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.logCollection'
system_updates_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.patch'
security_configurations_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.baseline'
endpoint_protection_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.antimalware'

disk_encryption_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.diskEncryption'

network_security_groups_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.nsgs'
    
web_application_firewall_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.waf'

vulnerability_assessment_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.vulnerabilityAssessment'
x
next_generation_firewall_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.ngfw'

storage_encryption_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.storageEncryption'

just_in_time_access_to_networks_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.jitNetworkAccess'
x
adaptive_application_controls_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.appWhitelisting'

sql_auditing_and_threat_detection_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.sqlAuditing'

sql_encryption_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.recommendations.sqlTde'

security_contact_email_is_set = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.securityContactConfiguration.securityContactEmails'

security_contact_phone_number_is_set = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.securityContactConfiguration.securityContactPhone'

send_email_alerts_is_on = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.securityContactConfiguration.areNotificationsOn'

send_email_to_subscription_owners = !az account get-access-token --query "{subscripton:subscription,accessToken:accessToken}" --out tsv | xargs -L1 bash -c 'curl -X GET -H "Authorization: Bearer $1" -H "Content-Type: application/json" https://management.azure.com/subscriptions/$0/providers/microsoft.Security/policies?api-version=2015-06-01-preview' | jq '.|.value[] | select(.name=="default")'|jq '.properties.securityContactConfiguration.sendToAdminOn'
