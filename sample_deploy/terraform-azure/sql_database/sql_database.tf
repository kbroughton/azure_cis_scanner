resource "azurerm_resource_group" "scannerTestSqlRg" {
  name     = "scannerTestSqlRg"
  location = "West US 2"
}

resource "random_id" "server" {
  keepers = {
    ami_id = 1
  }
  byte_length = 8
}

resource "azurerm_sql_server" "scannerTestSqlServer" {
    name = "${format("%s%s", "kv", random_id.server.dec)}" 
    resource_group_name = "${azurerm_resource_group.scannerTestSqlRg.name}"
    location = "West US 2"
    version = "12.0"
    administrator_login = "${var.administrator_login}"
    administrator_login_password = "${var.administrator_login_password}"
}

resource "azurerm_sql_database" "scannerTestSqlDb" {
  name                = "${format("%s-%s", "scanner-sqldb", random_id.server.dec)}"
  resource_group_name = "${azurerm_resource_group.scannerTestSqlRg.name}"
    location = "West US 2"
    server_name = "${azurerm_sql_server.scannerTestSqlServer.name}"

  tags {
    environment = "production"
  }
}

module "monitoring" {
  source = "../logging_monitoring"
}

resource "azurerm_metric_alertrule" "storage" {
  name = "${azurerm_sql_database.scannerTestSqlDb.name}-storage"
  resource_group_name = "${module.monitoring.monitorResourceGroupName}"
  location = "${module.monitoring.monitorResourceGroupLocation}"

  description = "An alert rule to watch the metric Storage"

  enabled = true

  resource_id = "${azurerm_sql_database.scannerTestSqlDb.id}"
  metric_name = "storage"
  operator = "GreaterThan"
  threshold = 1073741824
  aggregation = "Maximum"
  period = "PT10M"

  email_action {
    send_to_service_owners = false
    custom_emails = [
      "${module.monitoring.alert_email}",
    ]
  }

  webhook_action {
    service_uri = "https://example.com/some-url"
      properties = {
        severity = "incredible"
        acceptance_test = "true"
      }
  }
}