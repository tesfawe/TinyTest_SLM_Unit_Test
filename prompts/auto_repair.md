AUTO_REPAIR_TEMPLATE_v1 = """Fix only the failing test functions in the given pytest file, based on the error logs. Newly generate file should contain newly fixed and prevously correct ones. 

Module name: {module_name}
Function name: {function_name}

Function under test:
{code}

Failing test functions (to fix only these):
{failing_tests}

Pytest failure log:
{pytest_log}

RULES:
1. Keep all passing tests unchanged.
2. Fix only the failing tests using the error messages above.
3. Start the output with: from data.modules.{module_name} import {function_name}
4. Do not include markdown, explanations, or comments.

Output only the final repaired test file content below:
"""
