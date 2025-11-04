ZERO_SHOT_TEMPLATE_v1 = """You are a Python testing expert. Write pytest unit tests for the following function.

FUNCTION:
{code}

CRITICAL RULES:
1. Do NOT redefine the function
2. Start IMMEDIATELY with: from data.modules.{module_name} import {function_name}
3. Do NOT include markdown code fences (no ```)
4. Do NOT include explanations or comments
5. Write 4-6 test functions with names like: test_description_of_what_is_tested
6. Each test should use assert statements
7. Cover: normal cases, edge cases, empty inputs, and boundary values

BEGIN CODE BELOW:
"""
