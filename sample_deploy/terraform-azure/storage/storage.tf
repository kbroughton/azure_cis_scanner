resource "azurerm_resource_group" "scannerTestRg" {
  name     = "scannerStorageRg"
  location = "West US 2"
}

resource "azurerm_storage_account" "scannerStorageTestSA" {
  name                     = "storageaccountname${var.suffix}"
  resource_group_name      = "${azurerm_resource_group.scannerTestRg.name}"
  location                 = "West US 2"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = "${module.common.tags}"
}

module "common" {
  source = "../common"
}

# data "null_data_source" "extra_details" {
#   inputs = {
#     submitted = "${timestamp()}"
#   }
# }

# https://blog.aurynn.com/2017/2/23-fun-with-terraform-template-rendering
# https://blog.aurynn.com/2017/2/26-more-fun-with-terraform-templates
# data "template_file" "storageVars" {
#   template = "${file(${path.module}/storage_vars.tpl)}"

#   vars {
#     tf_apply_time = "${timestamp()}"
#   }
# }


data "azurerm_storage_account_sas" "scannerTestSecure" {
    connection_string = "${azurerm_storage_account.scannerStorageTestSA.primary_connection_string}"
    https_only        = true
    resource_types {
        service   = true
        container = false
        object    = false
    }
    services {
        blob  = true
        queue = false
        table = false
        file  = false
    }
    start   = "${var.start_time}"
    expiry  = "${var.end_time}"
    permissions {
        read    = true
        write   = true
        delete  = false
        list    = false
        add     = true
        create  = true
        update  = false
        process = false
    }
    

}

data "azurerm_storage_account_sas" "scannerTestInsecure" {
    connection_string = "${azurerm_storage_account.scannerStorageTestSA.primary_connection_string}"
    https_only        = false
    resource_types {
        service   = true
        container = false
        object    = false
    }
    services {
        blob  = true
        queue = true
        table = true
        file  = true
    }
    start   = "${var.start_time}"
    expiry  = "${var.late_end_time}"
    permissions {
        read    = true
        write   = true
        delete  = false
        list    = false
        add     = true
        create  = true
        update  = false
        process = false
    }
}

resource "azurerm_storage_container" "test" {
  name                  = "vhds"
  resource_group_name   = "${azurerm_resource_group.scannerTestRg.name}"
  storage_account_name  = "${azurerm_storage_account.scannerStorageTestSA.name}"
  container_access_type = "private"
}


resource "azurerm_storage_blob" "testsb" {
  name = "sample.vhd"

  resource_group_name    = "${azurerm_resource_group.scannerTestRg.name}"
  storage_account_name   = "${azurerm_storage_account.scannerStorageTestSA.name}"
  storage_container_name = "${azurerm_storage_container.test.name}"

  type = "page"
  size = 5120
}

resource "azurerm_storage_share" "testshare" {
  name = "sharename"

  resource_group_name  = "${azurerm_resource_group.scannerTestRg.name}"
  storage_account_name = "${azurerm_storage_account.scannerStorageTestSA.name}"

  quota = 50
}

resource "azurerm_storage_table" "test" {
  name                 = "mysampletable"
  resource_group_name  = "${azurerm_resource_group.scannerTestRg.name}"
  storage_account_name = "${azurerm_storage_account.scannerStorageTestSA.name}"
}

output "sas_url_query_string" {
  value = "${data.azurerm_storage_account_sas.scannerTestSecure.sas}"
}

