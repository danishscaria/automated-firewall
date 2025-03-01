"""
update_azure_firewall.py

This module integrates the output of a Z3‑based firewall optimizer with Azure Firewall.
It:
  1. Retrieves the optimized firewall allocation from the optimization model.
  2. Constructs a list of network rules based on the optimization.
  3. Updates an Azure Firewall network rule collection using the Azure SDK for Python.

Usage:
  Run this script to update your Azure Firewall configuration with optimized rules.
"""
import unittest
import datetime
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from MyFirewallFunctionProj.firewall_optimizer import optimize_firewalls

# Replace these with your actual Azure subscription and resource details.
SUBSCRIPTION_ID = "c4a7542d-5884-4ab6-a0f3-d18cac5525eb"
RESOURCE_GROUP = "MyResourceGroup"
FIREWALL_NAME = "myAzureFirewall"
RULE_COLLECTION_NAME = "AllowRules"   # Name of the rule collection to update
PRIORITY = 100                        # Priority for the rule collection

def update_azure_firewall():
    # Step 1: Run the optimization model.
    result = optimize_firewalls()
    print("Optimization result:", result)

    # Step 2: Build a list of network rules based on optimization output.
    rules = []
    # Example: For 'frontend', if a firewall is deployed, add a rule to block SSH traffic.
    if result["firewall_allocation"].get("frontend", False):
        rules.append({
            "name": "BlockSSH",
            "protocols": ["TCP"],
            "source_addresses": ["*"],
            "destination_addresses": ["20.169.181.2"],  # Replace with target IP address
            "destination_ports": ["22"]
        })
    # Example: For 'backend', if a firewall is deployed, add a rule to allow HTTP traffic.
    if result["firewall_allocation"].get("backend", False):
        rules.append({
            "name": "AllowHTTP",
            "protocols": ["TCP"],
            "source_addresses": ["*"],
            "destination_addresses": ["20.169.181.2"],  # Replace with target IP address
            "destination_ports": ["80"]
        })
    # Example: For 'dmz', if a firewall is deployed and the allow rule is required, add a rule for HTTPS.
    if result["firewall_allocation"].get("dmz", False) and result.get("allow_rule_dmz_backend", False):
        rules.append({
            "name": "AllowHTTPS",
            "protocols": ["TCP"],
            "source_addresses": ["*"],
            "destination_addresses": ["20.169.181.2"],  # Replace with target IP address
            "destination_ports": ["443"]
        })

    # Step 3: Authenticate with Azure and create a Network Management client.
    credential = DefaultAzureCredential()
    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

    # Step 4: Build the list of NetworkRule objects.
    from azure.mgmt.network import (
        NetworkRule,
        NetworkRuleCollection,
        RuleCollectionType
    )
    network_rules = []
    for rule in rules:
        network_rule = NetworkRule(
            name=rule["name"],
            protocols=rule["protocols"],
            source_addresses=rule["source_addresses"],
            destination_addresses=rule["destination_addresses"],
            destination_ports=rule["destination_ports"]
        )
        network_rules.append(network_rule)

    # Step 5: Create or update the network rule collection.
    rule_collection = NetworkRuleCollection(
        name=RULE_COLLECTION_NAME,
        priority=PRIORITY,
        action={"type": "Allow"},  # Change to "Deny" if desired.
        rules=network_rules,
        rule_collection_type=RuleCollectionType.NetworkRule
    )

    # Step 6: Retrieve the current Azure Firewall configuration.
    firewall = network_client.azure_firewalls.get(RESOURCE_GROUP, FIREWALL_NAME)
    print("Retrieved firewall configuration.")

    # Step 7: Update the firewall's network rule collections.
    # We'll replace (or add) the collection with our new rules.
    updated_collections = []
    collection_found = False
    if firewall.network_rule_collections:
        for col in firewall.network_rule_collections:
            if col.name == RULE_COLLECTION_NAME:
                updated_collections.append(rule_collection)
                collection_found = True
            else:
                updated_collections.append(col)
    if not collection_found:
        updated_collections.append(rule_collection)

    firewall.network_rule_collections = updated_collections

    # Step 8: Update the firewall with the new configuration.
    print("Updating Azure Firewall...")
    poller = network_client.azure_firewalls.begin_create_or_update(RESOURCE_GROUP, FIREWALL_NAME, firewall)
    updated_firewall = poller.result()
    print("Firewall updated successfully at", datetime.datetime.utcnow().isoformat())

    # Display the updated rule collections.
    for col in updated_firewall.network_rule_collections:
        print(f"Rule Collection: {col.name}, Priority: {col.priority}")
        for r in col.rules:
            print(f"  - {r.name}: {r.protocols} {r.destination_ports}")

if __name__ == "__main__":
    update_azure_firewall()
