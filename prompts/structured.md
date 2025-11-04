STRUCTURED_TEMPLATE_v1 = """Generate pytest tests for the function below.

FUNCTION CODE:
{code}

IMPORT:
from data.modules.{module_name} import {function_name}

TEST STRUCTURE:
def test_normal_case():
    assert {function_name}(...) == expected

def test_edge_case():
    assert {function_name}(...) == expected

def test_empty_input():
    assert {function_name}(...) == expected

def test_special_case():
    assert {function_name}(...) == expected

REQUIREMENTS:
- Output only valid Python code
- No markdown, comments, or explanations
- Use the exact import above
- Create 4–6 test functions using assert
- Cover normal, edge, empty, and special inputs

BEGIN CODE NOW:
"""
