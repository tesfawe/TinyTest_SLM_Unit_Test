ZERO_SHOT_TEMPLATE_v1 = """You are a Python testing expert. Write pytest unit tests for the function shown below. Test only the behavior that is explicitly implemented in the function code. Do not invent or assume any extra validation, behavior, or error handling like TypeError, ValueError.

**Must Follow**: Write maximum 6 test functions and 2-3 assertion logic with with names like: test_description_of_what_is_tested. Only call the imported function with suitable parameter values.


FUNCTION:
{code}

CRITICAL RULES:
1. Do NOT redefine the function
2. Start IMMEDIATELY with: from data.modules.{module_name} import {function_name}
3. Do NOT include markdown code fences (no ```)
4. Do NOT include explanations or comments
5. Each test should use assert statements
6. Cover normal use cases, small edge cases, and boundary values within valid input ranges.

BEGIN CODE BELOW:
"""
