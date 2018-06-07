
RESOURCE_GROUP_1=cis_scanner_rg1_`date "+%Y-%m-%d"`
RESOURCE_GROUP_2=cis_scanner_rg2_`date "+%Y-%m-%d"`
LOCATION=centralus
VAULT_NAME=cis-key-vault

echo "Ensure you are running against the correct subscription"
az account show

echo "Using values"
echo "RESOURCE_GROUP_1: ${RESOURCE_GROUP_1}"
echo "RESOURCE_GROUP_2: ${RESOURCE_GROUP_2}"
echo "LOCATION: ${LOCATION}"

echo "Pausing 10 seconds.  Ctrl + c to quit"
#sleep 10

#cis-asdf-1234
#cis-asdf-1234A
#cisstorage5

#echo "Creating resource group ${RESOURCE_GROUP_2}"
#az group create -l ${LOCATION} --name ${RESOURCE_GROUP_1} --tags 'env=test ttl_days=1 billing=internal'

################################
# Django App with SQL Backend
################################
echo "Creating Django app with SQL backend"
#az config mode arm
az group deployment create --resource-group ${RESOURCE_GROUP_1} --name cis_test_django_sql --template-uri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/sqldb-django-on-ubuntu/azuredeploy.json

echo "Finished Django"
#sleep 100
###############
# Jenkins CI/CD
###############
echo "Creating Jenkins CI/CD"
#az config mode arm
az group deployment create --resource-group ${RESOURCE_GROUP_1} --name cis_test_jenkins --template-uri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/cloudbeesjenkins-dockerdatacenter/azuredeploy.json


###############################################################
# Deploy VM in VNet with LB and configure as Domain Controller
###############################################################
echo "Creating domain controller"

#az config mode arm
az group deployment create --resource-group ${RESOURCE_GROUP_1} --name cis_test_domain_controller --template-uri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/active-directory-new-domain/azuredeploy.json


####################################
# Encrypt a running vm without AAD
####################################
echo "Encrypt a running vm without AAD"
#az config mode arm
az group deployment create --resource-group ${RESOURCE_GROUP_1} --name cis_test_encrypt_vm --template-uri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/201-encrypt-running-windows-vm-without-aad/azuredeploy.json


################################
# Django App with SQL Backend
################################
echo "Creating Django app with SQL backend"
#az config mode arm
az group deployment create --resource-group ${RESOURCE_GROUP_1} --name cis_test_django_sql --template-uri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/sqldb-django-on-ubuntu/azuredeploy.json


################################
# Deploy a Key Vault
################################

az keyvault create \
  --name ${VAULT_NAME} \
  --resource-group ${RESOURCE_GROUP_1} \
  --location ${LOCATION} \
  --enabled-for-template-deployment true
az keyvault secret set --vault-name ${VAULT_NAME} --name cis-examplesecret --value cis-super-secret