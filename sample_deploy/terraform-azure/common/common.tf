data "azurerm_subscription" "current" {
    
}




data "azurerm_client_config" "current" {

}

resource "azurerm_resource_group" "defaultRG" {
  name     = "scannerDefaultResourceGroup"
  location = "West US 2"
}

resource "random_id" "random" {
  byte_length = 8
}
# output "account_id" {
#   value = "${data.azurerm_client_config.current.service_principal_application_id}"
# }


output "defaultRGName" {
    value = "${azurerm_resource_group.defaultRG.name}"
}

output "defaultRGLocation" {
    value = "${azurerm_resource_group.defaultRG.location}"
}


output "current_subscription_display_name" {
  value = "${data.azurerm_subscription.current.display_name}"
}

output "tags" {
    value = "${var.tags}"
}

output "random_b64" {
    value = "${random_id.random.b64_std}"
}