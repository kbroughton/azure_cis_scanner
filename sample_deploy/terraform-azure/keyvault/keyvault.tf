

resource "random_id" "server" {
  keepers = {
    ami_id = 1
  }
  byte_length = 8
}

module "common" {
  source = "../common"
}

resource "azurerm_key_vault" "test" {
  name                = "scannerTestvault"
  location            = "${module.common.defaultRGLocation}"
  resource_group_name = "${module.common.defaultRGName}"

  sku {
    name = "standard"
  }

  tenant_id = "${var.tenant_id}"

  access_policy {
    tenant_id = "${var.tenant_id}"
    object_id = "${var.object_id}"

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

resource "azurerm_key_vault_key" "generated" {
  name      = "scanner-test-generated-certificate"
  vault_uri = "${azurerm_key_vault.test.vault_uri}"
  key_type  = "RSA"
  key_size  = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
}