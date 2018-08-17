resource "azurerm_resource_group" "scannerLogingMonitoring" {
  name     = "scanner_test_analytics"
  location = "westeurope"
}

resource "random_id" "workspace" {
  keepers = {
    # Generate a new id each time we switch to a new resource group
    group_name = "${azurerm_resource_group.scannerLogingMonitoring.name}"
  }

  byte_length = 8
}

# resource "azurerm_log_analytics_workspace" "test" {
#   name                = "scanner-workspace-${random_id.workspace.hex}"
#   location            = "${azurerm_resource_group.scannerLogingMonitoring.location}"
#   resource_group_name = "${azurerm_resource_group.scannerLogingMonitoring.name}"
#   sku                 = "Free"
# }

# resource "azurerm_log_analytics_solution" "test" {
#   solution_name         = "Containers"
#   location              = "${azurerm_resource_group.scannerLogingMonitoring.location}"
#   resource_group_name   = "${azurerm_resource_group.scannerLogingMonitoring.name}"
#   workspace_resource_id = "${azurerm_log_analytics_workspace.test.id}"
#   workspace_name        = "${azurerm_log_analytics_workspace.test.name}"

#   plan {
#     publisher = "Microsoft"
#     product   = "OMSGallery/Containers"
#   }
# }


output "monitorResourceGroupName" {
  value = "${azurerm_resource_group.scannerLogingMonitoring.name}"
}

output "monitorResourceGroupLocation" {
  value = "${azurerm_resource_group.scannerLogingMonitoring.location}"
}

output "alert_email" {
  value = "${var.alert_email}"
}