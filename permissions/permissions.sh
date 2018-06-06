#!/bin/bash

###############################################################
# Create role and assign to testers
###############################################################

az role definition create --role-definition minimal_tester_role.json 

# Get 
# should be able to associate, but doesn't seem possible with custom role?
# Get principal names with 
# az ad user list
# az role association create --role AzureSecurityScanner --assignee <user_principals>

################################################################
# GENERATE SECURE STORAGE ACCESS SIGNATURES - temp credentials
################################################################

START_DATE=2018-05-27
END_DATE=2018-06-04
WHITELIST_IP=104.197.216.6

# Uncomment for debugging
#set -x

SUBSCRIPTIONS=$(az account list | jq '.[].id'| sed  's/"//g')

# Over-ride subscriptions with a space separated list inside the quotes if you must
#SUBSCRIPTIONS="55555555-xxxx-3333-bbbb-1111111111 444444..."

echo "Found Subscriptions ${SUBSCRIPTIONS}"

RESOURCE_GROUPS=$(for sub in $SUBSCRIPTIONS;do az account set --subscription $sub && az storage account list | jq '.[].resourceGroup' | sed 's/"//g'; done)

STORAGE_ACCOUNTS=$(for sub in $SUBSCRIPTIONS;do az account set --subscription $sub && az storage account list | jq '.[].name' | sed 's/"//g'; done)

KEYS=$(for ((i=0;i<${#STORAGE_ACCOUNTS[@]};++i)); do az storage account keys list --resource-group "${RESOURCE_GROUPS[i]}"  --account-name "${STORAGE_ACCOUNTS[i]}" | jq '.[].value' | sed 's/"//g' | head -n 1; done)

# Grant a SAS token for resource-types=(s)ervice,(c)ontainer,(o)bject for services=(b)lob,(f)ile,(t)able,(q)ueue with permission=(l)ist

for ((i=0;i<${#STORAGE_ACCOUNTS[@]};++i)); do
  printf "${RESOURCE_GROUPS[i]} ${STORAGE_ACCOUNTS[i]} "
  az storage account generate-sas \
           --start ${START_DATE} \
           --expiry ${END_DATE} \
           --permissions l \
           --resource-types sco \
           --services bftq \
           --account-name ${STORAGE_ACCOUNTS[i]} \
           --account-key ${KEYS[i]} \
           --ip ${WHITELIST_IP} | sed 's/"//g'
done

