resource "azurerm_resource_group" "scanner_test" {
  name     = "azsanner_vm_rg"
  location = "West US 2"
}

resource "azurerm_virtual_network" "test" {
  name                = "azscanner_vm_net"
  address_space       = ["10.0.0.0/16"]
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"

  tags = "${var.tags}"

}

resource "azurerm_subnet" "test" {
  name                 = "azscanner_vm_subnet"
  resource_group_name  = "${azurerm_resource_group.scanner_test.name}"
  virtual_network_name = "${azurerm_virtual_network.test.name}"
  address_prefix       = "10.0.2.0/24"
}

resource "azurerm_network_interface" "test" {
  name                = "azscanner_vm_nic"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = "${azurerm_subnet.test.id}"
    private_ip_address_allocation = "dynamic"
  }
  tags = "${var.tags}"

}

resource "azurerm_managed_disk" "test" {
  name                 = "azscanner_datadisk_existing"
  location             = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name  = "${azurerm_resource_group.scanner_test.name}"
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "10"

  tags = "${var.tags}"
}

resource "azurerm_virtual_machine" "test" {
  name                  = "azscanner_vm_ubuntu"
  location              = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name   = "${azurerm_resource_group.scanner_test.name}"
  network_interface_ids = ["${azurerm_network_interface.test.id}"]
  vm_size               = "Standard_DS1_v2"

  # Uncomment this line to delete the OS disk automatically when deleting the VM
  # delete_os_disk_on_termination = true

  # Uncomment this line to delete the data disks automatically when deleting the VM
  # delete_data_disks_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"

  }

  # Optional data disks
  storage_data_disk {
    name              = "datadisk_new"
    managed_disk_type = "Standard_LRS"
    create_option     = "Empty"
    lun               = 0
    disk_size_gb      = "10"

  }

  storage_data_disk {
    name            = "${azurerm_managed_disk.test.name}"
    managed_disk_id = "${azurerm_managed_disk.test.id}"
    create_option   = "Attach"
    lun             = 1
    disk_size_gb    = "${azurerm_managed_disk.test.disk_size_gb}"

  }



  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin-${module.common.random_b64}"
    admin_password = "Password1234!-${module.common.random_b64}"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  tags = "${var.tags}"
}

module "common" {
  source = "../common"
}


resource "azurerm_metric_alertrule" "cpu" {
  name = "${azurerm_virtual_machine.test.name}-cpu"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  location = "${azurerm_resource_group.scanner_test.location}"

  description = "An alert rule to watch the metric Percentage CPU"

  enabled = true

  resource_id = "${azurerm_virtual_machine.test.id}"
  metric_name = "Percentage CPU"
  operator = "GreaterThan"
  threshold = 75
  aggregation = "Average"
  period = "PT5M"

  email_action {
    send_to_service_owners = false
    custom_emails = [
      "${var.alert_email}",
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

#########################################
# Windows VM with data disk from snapshot
#########################################

resource "azurerm_network_interface" "windows-workstation_nic" {
  name                = "azscanner-nic"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"


  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = "${azurerm_subnet.test.id}"
    private_ip_address_allocation = "dynamic"
  }
}

resource "azurerm_network_interface" "windows-workstation_nic2" {
  name                = "azscanner-nic2"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"


  ip_configuration {
    name                          = "testconfiguration2"
    subnet_id                     = "${azurerm_subnet.test.id}"
    private_ip_address_allocation = "dynamic"
  }
}


resource "azurerm_managed_disk" "source" {
  name                 = "azscanner-windows-workstation-disk"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  storage_account_type = "Standard_LRS"
  create_option = "Empty"
  disk_size_gb = "30"

  tags = "${module.common.tags}"
}


resource "azurerm_managed_disk" "copy" {
  name                 = "azscanner-windows-workstation-disk-snap"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  storage_account_type = "Standard_LRS"
  create_option = "Copy"
  source_resource_id = "${azurerm_snapshot.azscannerManagedDisk.id}"
  disk_size_gb =  "${azurerm_snapshot.azscannerManagedDisk.disk_size_gb}"

  tags = "${module.common.tags}"

}

module "keyvault" {
  source = "../keyvault"
}

resource "azurerm_managed_disk" "encrypted-copy" {
  name                 = "azscanner-windows-workstation-disk-snap-encrypted"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  storage_account_type = "Standard_LRS"
  create_option = "Copy"
  source_resource_id = "${azurerm_snapshot.azscannerManagedDisk.id}"
  disk_size_gb = "${azurerm_snapshot.azscannerManagedDisk.disk_size_gb}"

  tags = "${module.common.tags}"
  encryption_settings = {
    enabled = true
    disk_encryption_key = {
      secret_url = "${module.keyvault.disk_encryption_sercret_url}"
      source_vault_id = "${module.keyvault.keyvault_id}"
    }
  }

}

## Workstation machine
resource "azurerm_virtual_machine" "windows-workstation" {
  name                  = "windows-workstation"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  vm_size               = "Standard_D2s_v3"
  network_interface_ids = ["${azurerm_network_interface.windows-workstation_nic2.id}"]

  storage_os_disk {
    name              = "${azurerm_managed_disk.source.name}"
    os_type           = "windows"
    managed_disk_id   = "${azurerm_managed_disk.source.id}"
    create_option     = "Attach"
    disk_size_gb = "${azurerm_managed_disk.source.disk_size_gb}"

  }

  storage_data_disk {
    lun                  = 0
    create_option = "Empty"
    disk_size_gb = 20
    name = "azscanner-windows-unmanaged-disk"
  }

# Attaching encrypted disk seems to be a PR waiting for merge
#https://github.com/terraform-providers/terraform-provider-azurerm/issues/486

  # storage_data_disk {
  #   lun                  = 1
  #   name = "${azurerm_managed_disk.encrypted-copy.name}"
  #   create_option = "Attach"
  #   managed_disk_id = "${azurerm_managed_disk.encrypted-copy.id}"
  #   disk_size_gb = "${azurerm_managed_disk.encrypted-copy.disk_size_gb}"
  # }
}

################################
# Snapshot
################################

resource "azurerm_managed_disk" "azscannerManagedDisk" {
  name                 = "managed-disk"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 10
}

resource "azurerm_snapshot" "azscannerManagedDisk" {
  name                = "snapshot"
  location            = "${azurerm_resource_group.scanner_test.location}"
  resource_group_name = "${azurerm_resource_group.scanner_test.name}"
  create_option       = "Copy"
  source_uri          = "${azurerm_managed_disk.azscannerManagedDisk.id}"
}

output "windows_snapshot" {
  value = "${azurerm_snapshot.azscannerManagedDisk.id}"
}
