#!/usr/bin/env python3

import sys
from pysros.management import connect
from datetime import datetime

connection = connect()

interfaces_path = '/nokia-conf:configure/router[router-name="Base"]'

# Create timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = 'cf3:\post-commit-results_' + timestamp + '.txt'

output = []
output.append("\n" + "="*70)
output.append("SUCCESS: All configuration changes have been applied successfully!")
output.append("="*70)
output.append("Timestamp: " + str(datetime.now()))
output.append("Committed configuration is now active on the router.")

# Get all interfaces from running (committed) configuration
router_config = connection.running.get(interfaces_path)

if 'interface' in router_config:
    interfaces_data = router_config['interface']
    
    allowed_prefixes = ["to_", "system", "loopback", "lo"]
    compliant = []
    non_compliant = []
    
    output.append("\nInterface Summary (Naming Convention Compliance):")
    output.append("-" * 70)
    
    for interface_name in sorted(interfaces_data.keys()):
        is_valid = any(interface_name.startswith(prefix) for prefix in allowed_prefixes)
        if is_valid:
            compliant.append(interface_name)
            msg = "  [OK] " + interface_name
            output.append(msg)
        else:
            non_compliant.append(interface_name)
            msg = "  [FAIL] " + interface_name
            output.append(msg)
    
    output.append("-" * 70)
    output.append("Total compliant interfaces: " + str(len(compliant)))
    output.append("Total non-compliant interfaces: " + str(len(non_compliant)))
else:
    msg = "\nNo interfaces found in configuration."
    output.append(msg)

output.append("\n" + "="*70 + "\n")

# Print output to console
for line in output:
    print(line)

# Write to file on cf3
try:
    with open(results_file, 'w') as f:
        for line in output:
            f.write(line + '\n')
except Exception as e:
    pass