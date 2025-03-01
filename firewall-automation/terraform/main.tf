// terraform/main.tf

// Create Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

// Create Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = var.address_space
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

// Create Subnets
resource "azurerm_subnet" "subnets" {
  for_each           = { for s in var.subnets : s.name => s }
  name               = each.value.name
  resource_group_name = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [each.value.address_prefix]
}

// Deploy Azure Firewall (or use NSGs as allocation places)
resource "azurerm_firewall" "fw" {
  name                = "azure-firewall"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku_name = "AZFW_VNet"
  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.subnets["dmz"].id
    public_ip_address_id = azurerm_public_ip.fw_public_ip.id
  }
}

resource "azurerm_public_ip" "fw_public_ip" {
  name                = "fw-public-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}
