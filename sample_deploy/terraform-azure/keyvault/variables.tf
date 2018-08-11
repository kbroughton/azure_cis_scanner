variable "tenant_id" {
  description = "The Prefix used for all resources in this example"
  default = "06fbf4a8-34be-4de2-800d-b60b4b8e4610"
}

variable "object_id" {
  description = "The Azure Region in which the resources in this example should exist"
  default = "0aa71df2-4f2b-4990-98ba-f7b224a841ab"
}

variable "tags" {
  type        = "map"
  default     = {}
  description = "Any tags which should be assigned to the resources in this example"
}

