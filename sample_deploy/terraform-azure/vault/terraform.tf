

module "vault" {
  source  = "hashicorp/vault/azurerm"
  version = "0.0.2"

  # insert the 10 required variables here
  allowed_inbound_cidr_blocks = "64.129.54.194/32"
}


