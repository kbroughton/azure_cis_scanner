variable "alert_email" {
  default     = "123@example.com"
  description = "email for sending alerts"
}

variable "tags" {
  default = {
    environment = "dev"
    client = "internal"
    billing = "internal"
    project = "azure_scanner"
  }

}