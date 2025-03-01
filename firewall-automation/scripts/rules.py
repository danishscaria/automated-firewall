firewall_rules = [
    {
        "name": "BlockSSH",
        "protocols": ["TCP"],
        "source_addresses": ["*"],
        "destination_addresses": ["20.169.181.2"],
        "destination_ports": ["22"],
        "priority": 1001,
        "action": "Deny"
    },
    {
        "name": "AllowHTTP",
        "protocols": ["TCP"],
        "source_addresses": ["*"],
        "destination_addresses": ["20.169.181.2"],
        "destination_ports": ["80"],
        "priority": 1002,
        "action": "Allow"
    }
]
