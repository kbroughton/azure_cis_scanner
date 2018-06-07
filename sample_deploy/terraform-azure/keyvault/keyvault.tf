resource "azurerm_resource_group" "test" {
  name     = "resourceGroup1"
  location = "West US"
}

resource "azurerm_key_vault" "test" {
  name                = "testvault"
  location            = "West US"
  resource_group_name = "${azurerm_resource_group.test.name}"

  sku {
    name = "standard"
  }

  tenant_id = "d6e396d0-5584-41dc-9fc0-268df99bc610"

  access_policy {
    tenant_id = "d6e396d0-5584-41dc-9fc0-268df99bc610"
    object_id = "d746815a-0433-4a21-b95d-fc437d2d475b"

    key_permissions = [
      "get",
    ]

    secret_permissions = [
      "get",
    ]
  }

  enabled_for_disk_encryption = true

  tags {
    environment = "Production"
  }
}
