# Defines AUTO_REPAIR_TEMPLATE_v1

AUTO_REPAIR_TEMPLATE_v1 = r"""
You are an assistant that fixes failing pytest tests for a given Python module.

Task:
- Analyze the module under test and the failing pytest log.
- Produce a corrected pytest test file that thoroughly tests the function but avoids brittle or incorrect assertions.
- Prefer deterministic assertions over randomized property checks unless seeded.
- Ensure imports and test function names are valid and runnable by pytest.

Module name: {module_name}
Target function: {function_name}

Code under test:
```python
{code}
```

Previous failing test code:
```python
{previous_test}
```

Pytest failure log (for context):
```
{pytest_log}
```

CRITICAL RULES:
1. Start IMMEDIATELY with: from data.modules.{module_name} import {function_name}
2. Do NOT include markdown code fences (no ```)
3. Do NOT include explanations or comments
4. Do NOT redefine the function
5. Write 4-6 test functions with names like: test_description_of_what_is_tested
6. Each test should use assert statements
7. Cover: normal cases, edge cases, empty inputs, and boundary values

Output: a single Python test file content.
"""


