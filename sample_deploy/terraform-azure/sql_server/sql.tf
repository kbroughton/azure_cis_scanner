resource "azurerm_resource_group" "cis_test" {
  name     = "cis-test-rg"
  location = "West US"
}

resource "azurerm_sql_server" "cis_test" {
  name                         = "cisx123mysqlserver"
  resource_group_name          = "${azurerm_resource_group.cis_test.name}"
  location                     = "${azurerm_resource_group.cis_test.location}"
  version                      = "12.0"
  administrator_login          = "cisadministrator"
  administrator_login_password = "cis!thisIsDog11"

  tags {
    environment = "production"
  }
}

