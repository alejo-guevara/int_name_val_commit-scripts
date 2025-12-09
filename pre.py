#!/usr/bin/env python3

import sys
from pysros.management import connect
from datetime import datetime

connection = connect(use_existing_candidate=True)
#connection = connect()

interfaces_path = '/nokia-conf:configure/router[router-name="Base"]'

# Create timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = 'cf3:\pre-commit-results_' + timestamp + '.txt'

output = []
output.append("\n" + "="*70)
output.append("PRE-COMMIT INTERFACE NAMING VALIDATION")
output.append("="*70)
output.append("Timestamp: " + str(datetime.now()))

# Get all interfaces from candidate configuration
router_config = connection.candidate.get(interfaces_path)

if 'interface' in router_config:
    interfaces_data = router_config['interface']
    
    allowed_prefixes = ["to_", "system", "loopback", "lo"]
    passed = 0
    failed = 0
    failed_interfaces = []
    
    output.append("\nInterface Validation Details:")
    output.append("-" * 70)
    
    for interface_name in sorted(interfaces_data.keys()):
        is_valid = any(interface_name.startswith(prefix) for prefix in allowed_prefixes)
        if is_valid:
            msg = "  [PASS] " + interface_name
            output.append(msg)
            passed += 1
        else:
            msg = "  [FAIL] " + interface_name
            output.append(msg)
            failed += 1
            failed_interfaces.append(interface_name)
    
    output.append("-" * 70)
    output.append("Total interfaces: " + str(passed + failed))
    output.append("Passed: " + str(passed))
    output.append("Failed: " + str(failed))
    
    if failed > 0:
        output.append("\nERROR: Non-compliant interfaces detected:")
        for iface in failed_interfaces:
            output.append("  - " + iface)
        output.append("\nCOMMIT ABORTED: Fix interface naming convention before committing.")
    else:
        output.append("\nSUCCESS: All interfaces comply with naming convention.")
else:
    output.append("\nNo interfaces found in candidate configuration.")

output.append("\n" + "="*70 + "\n")

# Write to file on cf3
try:
    with open(results_file, 'w') as f:
        for line in output:
            f.write(line + '\n')
except:
    pass

# Print output to console
for line in output:
    print(line)

# Check for failures and abort
if 'interface' in router_config and failed > 0:
    raise SystemError("Non-compliant interfaces detected: " + ", ".join(failed_interfaces))