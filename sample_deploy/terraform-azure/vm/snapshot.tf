# module "common" {
#   source = "../common"
# }

# resource "azurerm_managed_disk" "test" {
#   name                 = "managed-disk"
#   location             = "${module.common.defaultRGLocation}"
#   resource_group_name  = "${module.common.defaultRGName}"
#   storage_account_type = "Standard_LRS"
#   create_option        = "Empty"
#   disk_size_gb         = "10"
# }

# resource "azurerm_snapshot" "test" {
#   name                = "snapshot"
#   location             = "${module.common.defaultRGLocation}"
#   resource_group_name  = "${module.common.defaultRGName}"
#   create_option       = "Copy"
#   source_uri          = "${azurerm_managed_disk.test.id}"
# }

# output "windows_snapshot" {
#   value = "${azurerm_snapshot.test.id}"
# }
