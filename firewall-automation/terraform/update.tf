# Create Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "MyResourceGroup"
  location = "eastus"
}

# Create Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "myVNet"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = ["10.0.0.0/16"]
}

# Create a dedicated subnet for Azure Firewall (must be named 'AzureFirewallSubnet')
resource "azurerm_subnet" "fw_subnet" {
  name                 = "AzureFirewallSubnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create a Public IP for the Firewall
resource "azurerm_public_ip" "fw_public_ip" {
  name                = "fw-public-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Deploy Azure Firewall
resource "azurerm_firewall" "fw" {
  name                = "myAzureFirewall"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku_name            = "AZFW_VNet"
}

# Configure Firewall IP Configuration
resource "azurerm_firewall_ip_configuration" "fw_ipconfig" {
  name                 = "configuration"
  resource_group_name  = azurerm_resource_group.rg.name
  firewall_name        = azurerm_firewall.fw.name
  subnet_id            = azurerm_subnet.fw_subnet.id
  public_ip_address_id = azurerm_public_ip.fw_public_ip.id
}

# Create a Network Rule Collection to filter traffic
resource "azurerm_firewall_network_rule_collection" "allow_rules" {
  name                = "AllowRules"
  resource_group_name = azurerm_resource_group.rg.name
  firewall_name       = azurerm_firewall.fw.name
  priority            = 100
  action              = "Allow"

  # Example rule: Allow SSH traffic to an internal VM
  rule {
    name                  = "AllowSSH"
    protocol              = "TCP"
    source_addresses      = ["*"]
    destination_addresses = ["10.0.2.4"]  # Replace with target IP address
    destination_ports     = ["22"]
  }

  # Example rule: Allow HTTP traffic to another internal VM
  rule {
    name                  = "AllowHTTP"
    protocol              = "TCP"
    source_addresses      = ["*"]
    destination_addresses = ["10.0.2.5"]  # Replace with target IP address
    destination_ports     = ["80"]
  }
}
