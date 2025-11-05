# Defines AUTO_REPAIR_TEMPLATE_v1

AUTO_REPAIR_TEMPLATE_v1 = r"""
Fix the failing tests below. Generate a complete pytest test file with corrected versions.

Module: {module_name}
Function: {function_name}

Code under test:
```python
{code}
```

Failing tests (fix these):
```python
{failing_tests}
```

Error details:
```
{pytest_log}
```

RULES:
1. Start: from data.modules.{module_name} import {function_name}
2. Fix the failing tests based on error log
3. Write a complete test file (4-6 test functions covering normal/edge cases)
4. No markdown, no comments
5. Output ONLY Python code
6. Do NOT redefine the function

Output: a single Python test file content.
"""


