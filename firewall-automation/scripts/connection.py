import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["firewall_db"]
collection = db["malicious_ips"]

# Sample IPs
malicious_ips = [{"ip_address": "192.168.1.100", "source": "AbuseIPDB", "confidence_score": 90},
                 {"ip_address": "203.0.113.25", "source": "Spamhaus", "confidence_score": 80}]

# Insert IPs into MongoDB
collection.insert_many(malicious_ips)

print("Malicious IPs stored in MongoDB")
