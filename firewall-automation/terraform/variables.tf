// terraform/variables.tf
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "firewall-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "vnet_name" {
  description = "Name of the virtual network"
  type        = string
  default     = "firewall-vnet"
}

variable "address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnets" {
  description = "Subnets definitions"
  type = list(object({
    name           = string
    address_prefix = string
  }))
  default = [
    { name = "frontend", address_prefix = "10.0.1.0/24" },
    { name = "backend", address_prefix = "10.0.2.0/24" },
    { name = "dmz", address_prefix = "10.0.3.0/24" }
  ]
}
