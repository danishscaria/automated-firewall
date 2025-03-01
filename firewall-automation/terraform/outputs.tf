// terraform/outputs.tf
output "vnet_id" {
  description = "The ID of the Virtual Network"
  value       = azurerm_virtual_network.vnet.id
}

output "firewall_public_ip" {
  description = "Public IP of the deployed Firewall"
  value       = azurerm_public_ip.fw_public_ip.ip_address
}
