

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
      "backup",
      "create",
      "decrypt",
      "delete",
      "encrypt",
      "get",
      "import",
      "list",
      "purge",
      "recover",
      "restore",
      "sign",
      "unwrapKey",
      "update",
      "verify",
      "wrapKey"
    ]

    secret_permissions = [
      "get",
      "backup",
      "set",
      "delete",
      "get",
      "list",
      "restore",
      "recover"
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

resource "random_id" "vault_id" {
  byte_length = 8
}

resource "azurerm_key_vault_secret" "test" {
  name      = "azscanner-disk-encryption-key"
  value     = "${random_id.vault_id.b64_std}"
  vault_uri = "${azurerm_key_vault.test.vault_uri}"

  tags = "${module.common.tags}"
  
}

output "disk_encryption_sercret_url" {
  value = "${azurerm_key_vault_secret.test.id}"
}

output "keyvault_uri" {
  value = "${azurerm_key_vault.test.vault_uri}"
}

output "keyvault_id" {
  value = "${azurerm_key_vault.test.id}"
}

output "tenant_id" {
  value = "${var.tenant_id}"
}

output "object_id" {
  value = "${var.object_id}"
}


