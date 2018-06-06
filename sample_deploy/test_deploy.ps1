test_deploy.ps1

Work in progress.

Use test_deploy.sh as a template.  We collect the equivalent powershell commands here.  Untested.



###############
# Jenkins CI/CD
###############

New-AzureRmResourceGroupDeployment -Name <deployment-name> -ResourceGroupName <resource-group-name> -TemplateUri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/cloudbeesjenkins-dockerdatacenter/azuredeploy.json


###############################################################
# Deploy VM in VNet with LB and configure as Domain Controller
###############################################################

New-AzureRmResourceGroupDeployment -Name <deployment-name> -ResourceGroupName <resource-group-name> -TemplateUri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/201-encrypt-running-windows-vm-without-aad/azuredeploy.json

####################################
# Encrypt a running vm without AAD
####################################

New-AzureRmResourceGroupDeployment -Name <deployment-name> -ResourceGroupName <resource-group-name> -TemplateUri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/201-encrypt-running-windows-vm-without-aad/azuredeploy.json

################################
# Django App with SQL Backend
################################

New-AzureRmResourceGroupDeployment -Name <deployment-name> -ResourceGroupName <resource-group-name> -TemplateUri https://raw.githubusercontent.com/azure/azure-quickstart-templates/master/sqldb-django-on-ubuntu/azuredeploy.json


################################
# Deploy a Key Vault
################################

New-AzureRmResourceGroup -Name datagroup -Location "South Central US"
New-AzureRmResourceGroupDeployment `
  -Name exampledeployment `
  -ResourceGroupName datagroup `
  -TemplateUri https://raw.githubusercontent.com/Azure/azure-docs-json-samples/master/azure-resource-manager/keyvaultparameter/sqlserver.json `
  -TemplateParameterFile sqlserver.parameters.json