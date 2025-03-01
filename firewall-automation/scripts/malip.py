
import requests
import json
import datetime
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import NetworkRule, NetworkRuleCollection, RuleCollectionType
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from pymongo import MongoClient

# Azure Configuration
SUBSCRIPTION_ID = "c4a7542d-5884-4ab6-a0f3-d18cac5525eb"
RESOURCE_GROUP = "MyResourceGroup"
FIREWALL_NAME = "myAzureFirewall"
RULE_COLLECTION_NAME = "BlockMaliciousIPs"
STORAGE_ACCOUNT_NAME = "myfirewallstorage12345"
STORAGE_ACCOUNT_KEY = "Uv0oK7k7XicuMAKYCrMRLu6ZjF+zFwmePtDDbWVCpiaegTh9pgV0itukkJDqQjR44Y6oo5d4kuRU+ASti412uw=="
TABLE_NAME = "BlockedIPs"

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "firewallDB"
MONGO_COLLECTION = "blockedIPs"

# Threat Intelligence Feeds
THREAT_FEEDS = {
    "Spamhaus": "https://www.spamhaus.org/drop/drop.txt",
    "FireHOL": "http://iplists.firehol.org/files/firehol_level1.netset",
    "AlienVault": "https://reputation.alienvault.com/reputation.data"
}

# Function to Fetch Malicious IPs
def fetch_malicious_ips():
    malicious_ips = set()

    try:
        # Fetch from Spamhaus
        response = requests.get(THREAT_FEEDS["Spamhaus"])
        if response.status_code == 200:
            for line in response.text.split("\n"):
                if line and not line.startswith(";"):
                    malicious_ips.add(line.strip())

        # Fetch from FireHOL
        response = requests.get(THREAT_FEEDS["FireHOL"])
        if response.status_code == 200:
            for line in response.text.split("\n"):
                if line and "." in line:
                    malicious_ips.add(line.strip())

        # Fetch from AlienVault
        response = requests.get(THREAT_FEEDS["AlienVault"])
        if response.status_code == 200:
            for line in response.text.split("\n"):
                if not line.startswith("#") and "\t" in line:
                    ip = line.split("\t")[0]
                    malicious_ips.add(ip)

        logging.info(f"Fetched {len(malicious_ips)} malicious IPs.")
    except Exception as e:
        logging.error(f"Error fetching threat feeds: {e}")

    return list(malicious_ips)

# Function to Update Azure Firewall Rules
def update_firewall_rules(malicious_ips):
    credential = DefaultAzureCredential()
    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

    # Convert IPs into firewall rules
    firewall_rules = [
        NetworkRule(
            name=f"Block_{ip.replace('.', '_')}",
            protocols=["TCP", "UDP"],
            source_addresses=["*"],
            destination_addresses=[ip],
            destination_ports=["*"]
        )
        for ip in malicious_ips[:100]  # Limit rules to 100 IPs to avoid Azure limits
    ]

    # Define Rule Collection
    rule_collection = NetworkRuleCollection(
        name=RULE_COLLECTION_NAME,
        priority=200,  # Ensure priority is correct (lower number = higher priority)
        action={"type": "Deny"},
        rules=firewall_rules,
        rule_collection_type=RuleCollectionType.NetworkRule
    )

    # Fetch Existing Firewall
    firewall = network_client.azure_firewalls.get(RESOURCE_GROUP, FIREWALL_NAME)

    # Update Rule Collections
    updated_collections = []
    existing_rule_found = False
    for collection in (firewall.network_rule_collections or []):
        if collection.name == RULE_COLLECTION_NAME:
            updated_collections.append(rule_collection)
            existing_rule_found = True
        else:
            updated_collections.append(collection)

    if not existing_rule_found:
        updated_collections.append(rule_collection)

    firewall.network_rule_collections = updated_collections

    # Apply Changes
    poller = network_client.azure_firewalls.begin_create_or_update(RESOURCE_GROUP, FIREWALL_NAME, firewall)
    poller.result()

    logging.info("✅ Malicious IPs successfully blocked in Azure Firewall!")

# Function to Store Blocked IPs in MongoDB
def store_blocked_ips_in_mongodb(malicious_ips):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # Prepare data for insertion
    data = [{"ip": ip, "blocked_at": datetime.datetime.utcnow()} for ip in malicious_ips]

    # Insert data into MongoDB
    collection.insert_many(data)
    logging.info("✅ Blocked IPs successfully stored in MongoDB!")

# Function to Store Blocked IPs in Azure Table Storage
def store_blocked_ips_in_azure_table(malicious_ips):
    table_service_client = TableServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
    table_client = table_service_client.get_table_client(table_name=TABLE_NAME)

    # Prepare data for insertion
    data = [{"PartitionKey": "BlockedIP", "RowKey": ip, "BlockedAt": datetime.datetime.utcnow().isoformat()} for ip in malicious_ips]

    # Insert data into Azure Table Storage
    for entity in data:
        table_client.upsert_entity(entity=entity, mode=UpdateMode.MERGE)
    logging.info("✅ Blocked IPs successfully stored in Azure Table Storage!")

# Main Execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("🔥 Fetching Malicious IPs...")
    
    malicious_ips = fetch_malicious_ips()
    if malicious_ips:
        logging.info(f"🚀 Updating Azure Firewall with {len(malicious_ips)} malicious IPs...")
        update_firewall_rules(malicious_ips)
        logging.info("💾 Storing blocked IPs in MongoDB...")
        store_blocked_ips_in_mongodb(malicious_ips)
        logging.info("💾 Storing blocked IPs in Azure Table Storage...")
        store_blocked_ips_in_azure_table(malicious_ips)
    else:
        logging.warning("⚠️ No malicious IPs fetched. Firewall update skipped.")