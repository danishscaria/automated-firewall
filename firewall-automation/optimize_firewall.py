from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import SecurityRule
from z3 import Optimize, Bool, If, sat

# Example NSR rules (this is a simplified illustration)
allow_ssh = Bool("allow_ssh")
deny_malicious = Bool("deny_malicious")

solver = Optimize()
solver.add(allow_ssh)      # Enforce SSH allowed rule
solver.add(Not(deny_malicious))  # Ensure malicious IP is blocked

# Objective: minimize number of enabled rules (as a proxy for cost)
solver.minimize(If(allow_ssh, 1, 0) + If(deny_malicious, 1, 0))

if solver.check() == sat:
    model = solver.model()
    print("Optimized configuration:")
    print("Allow SSH:", model.evaluate(allow_ssh))
    print("Deny malicious IP:", model.evaluate(deny_malicious))
else:
    print("No solution found!")



credential = DefaultAzureCredential()
subscription_id = "your_subscription_id"
resource_group = "firewall-automation-rg"
nsg_name = "myNetworkSecurityGroup"

network_client = NetworkManagementClient(credential, subscription_id)

# Suppose Z3 outputs that AllowSSH should be enabled and a deny rule for malicious IPs.
allow_ssh_rule = SecurityRule(
    name="AllowSSH",
    protocol="Tcp",
    source_address_prefix="192.168.1.0/24",  # Trusted subnet
    destination_address_prefix="*",
    access="Allow",
    direction="Inbound",
    priority=1001,
    source_port_range="*",
    destination_port_range="22"
)

# Update the NSG with the new rule
async_update = network_client.security_rules.begin_create_or_update(
    resource_group_name=resource_group,
    network_security_group_name=nsg_name,
    security_rule_name="AllowSSH",
    security_rule_parameters=allow_ssh_rule
)
result = async_update.result()
print("NSG updated:", result.as_dict())
