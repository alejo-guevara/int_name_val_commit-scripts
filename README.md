# pySROS Configuration Compliance Validation

Automated pre-commit and post-commit validation for Nokia SR OS configuration using pySROS. Enforce custom compliance policies, prevent common configuration mistakes, and maintain audit trails across all SR OS deployments.

## Overview

This project provides a framework for validating SR OS configurations against custom business logic and compliance rules **before** they are committed. Unlike syntax validation, this approach focuses on enforcing organizational policies such as:

- Interface naming conventions
- Routing policy compliance
- Service configuration standards
- Import/export policy validation
- Unauthorized configuration changes prevention

## Features

✅ **Pre-commit validation** – Inspect candidate configuration before commit  
✅ **Automatic commit abort** – Prevent non-compliant configurations from being deployed  
✅ **Post-commit logging** – Audit trail with timestamped results  
✅ **Built on pySROS 25.10.1** – Leverages official Nokia pre/post commit script support  
✅ **Configurable rules** – Easy to customize validation logic for your organization  
✅ **Real-time feedback** – Immediate notification of validation failures  

## Requirements

- Nokia SR OS 25.10 or later
- pySROS 25.10.1 or later
- Python 3.10+

## Installation

### 1. Download the Scripts

Copy the validation scripts to your SR OS device:

```bash
scp pre.py admin@<router-ip>:/cf3/
scp post.py admin@<router-ip>:/cf3/
```

### 2. Configure on SR OS

SSH into your SR OS device and configure the pre-commit and post-commit scripts:

```
/configure

system {
    management-interface {
        commit-management {
            pre-commit-script "validate" {
                admin-state enable
                location cf3:/pre.py
            }
            post-commit-script "post" {
                admin-state enable
                location cf3:/post.py
            }
        }
    }
}

commit
```

## Usage

### Pre-Commit Validation

When you attempt to commit, the validation script automatically runs:

```
A:admin@CE# commit

PRE-COMMIT INTERFACE NAMING VALIDATION
======================================================================
Interface Validation Details:
----------------------------------------------------------------------
  [PASS] to_VRF-200_PE-1
  [PASS] lo1
  [PASS] system
  [FAIL] wrong-name
----------------------------------------------------------------------
Total interfaces: 4
Passed: 3
Failed: 1

ERROR: Non-compliant interfaces detected:
  - wrong-name

COMMIT ABORTED: Fix interface naming convention before committing.

MINOR: MGMT_CORE #2507: Python execution failed - SystemError: 
Non-compliant interfaces detected: wrong-name
INFO: MGMT_CORE #2608: Commit script failed - commit not applied 
because of pre-commit script failure
```

### Post-Commit Logging

After a successful commit, the post-commit script logs the results:

```
A:admin@CE# commit

SUCCESS: All configuration changes have been applied successfully!
======================================================================
Interface Summary (Naming Convention Compliance):
----------------------------------------------------------------------
  [OK] to_VRF-200_PE-1
  [OK] lo1
  [OK] system
----------------------------------------------------------------------
Total compliant interfaces: 3
Total non-compliant interfaces: 0
```

## Customization

### Adding New Validation Rules

Edit the validation script (`validate_fixed.py`) to add custom validation logic:

```python
# Example: Add additional validation rules
allowed_prefixes = ["to_", "system", "loopback", "lo"]  # Modify as needed

# Add more validation checks:
# - Routing policy validation
# - Service configuration compliance
# - Import/export policy checks
```

### Modifying Allowed Prefixes

Update the `ALLOWED_PREFIXES` list in the validation script:

```python
allowed_prefixes = ["to_", "system", "loopback", "lo", "mgmt"]  # Add or remove prefixes
```

## How It Works

### Pre-Commit Script (`validate_fixed.py`)

1. **Connects** to the local SR OS device using `connect(use_existing_candidate=True)`
2. **Retrieves** all interfaces from the candidate configuration
3. **Validates** each interface name against configured prefixes
4. **Aborts** the commit by raising `SystemError` if validation fails
5. **Logs** results to a timestamped file for audit trail

### Post-Commit Script (`post.py`)

1. **Connects** to the local SR OS device
2. **Retrieves** all interfaces from the running (committed) configuration
3. **Logs** the final configuration state with timestamp
4. **Documents** compliant and non-compliant interfaces for audit purposes

## pySROS 25.10.1 Features

This solution is built on official Nokia pySROS 25.10.1 enhancements:

- **Pre/post commit script support** – Scripts execute automatically before and after commits
- **`use_existing_candidate` parameter** – Access uncommitted candidate configuration during validation
- **SystemError exception handling** – SR OS recognizes exceptions and aborts commits

Reference: [pySROS 25.10 Features](https://network.developer.nokia.com/static/sr/learn/pysros/latest/features/25.10.html)

## Audit Logging

Each validation attempt creates a timestamped log file:

```
cf3:\pre-commit-results_20251204_232929.txt
cf3:\post-commit-results_20251204_233020.txt
```

View logs with:

```
A:admin@CE# file show cf3:\pre-commit-results_20251204_232929.txt
```

## Error Handling

### Common Errors

**"Python execution failed - SystemError"**
- Indicates validation failed
- Check the error message for specific violations
- Fix the configuration and resubmit

**"Could not compile script"**
- Check for Python syntax errors
- Ensure file encoding is UTF-8
- Verify no problematic comment syntax (avoid f-strings in comments)

## Best Practices

1. **Test before deployment** – Test validation rules on a lab device first
2. **Document your rules** – Clearly document what compliance rules are enforced
3. **Review audit logs** – Regularly check timestamped logs for compliance tracking
4. **Update incrementally** – Add validation rules one at a time and test
5. **Communicate changes** – Notify users when validation rules change

## Examples

### Example 1: Interface Naming Validation

```python
allowed_prefixes = ["to_", "system", "loopback", "lo"]
# Enforces naming conventions:
# - Transit interfaces: to_*
# - System interface: system
# - Loopback interfaces: loopback* or lo*
```

### Example 2: Extending to Policy Validation

Modify the script to validate import/export policies:

```python
# Check that all VRFs have required import policies
required_policies = ["IMPORT_POLICY", "EXPORT_POLICY"]
for policy in required_policies:
    if policy not in router_config.get("service", {}):
        raise SystemError(f"Missing required policy: {policy}")
```

## Troubleshooting

### Script not triggering on commit

- Verify scripts are configured in `/configure system management-interface commit-management`
- Check that `admin-state` is enabled for both scripts
- Ensure file paths are correct (`cf3:/` syntax)
- Verify scripts have execute permissions

### Validation always passing when it shouldn't

- Check the candidate datastore is being queried correctly
- Verify `use_existing_candidate=True` is set in connect()
- Review the validation logic for edge cases
- Check that interface data is being retrieved

### Audit logs not being created

- Verify `cf3:\` path is correct
- Check file system permissions
- Ensure the directory exists
- Review error output for file write failures

## Contributing

To extend this project:

1. Add new validation rules to the scripts
2. Test thoroughly in a lab environment
3. Document any new configuration policies
4. Update this README with usage examples
5. Submit improvements via pull request

## License

This project is provided as-is for use with Nokia SR OS.

## References

- [pySROS Documentation](https://documentation.nokia.com/sr/25-10/pysros/introduction.html)
- [pySROS 25.10 Features](https://network.developer.nokia.com/static/sr/learn/pysros/latest/features/25.10.html)
- [Nokia SR OS Documentation](https://documentation.nokia.com)

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review validation log files
3. Enable debug logging in the scripts
4. Consult Nokia SR OS documentation

## Changelog

### Version 1.0 (2024-12-04)
- Initial release
- Pre-commit interface naming validation
- Post-commit audit logging
- Support for SR OS 25.10+
