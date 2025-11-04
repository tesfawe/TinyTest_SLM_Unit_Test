FEW_SHOT_TEMPLATE_v1 = """You are a Python testing expert. Generate pytest unit tests for the given function.

EXAMPLE 1:
Function to test:
```python
def add_numbers(a: int, b: int) -> int:
    return a + b
```

Correct test file:
```python
from data.modules.module_example import add_numbers

def test_add_positive_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(10, 20) == 30

def test_add_negative_numbers():
    assert add_numbers(-5, -3) == -8
    assert add_numbers(-10, 5) == -5

def test_add_zero():
    assert add_numbers(0, 0) == 0
    assert add_numbers(5, 0) == 5

def test_add_large_numbers():
    assert add_numbers(1000000, 2000000) == 3000000
```

EXAMPLE 2:
Function to test:
```python
def is_palindrome(s: str) -> bool:
    clean = ''.join(c.lower() for c in s if c.isalnum())
    return clean == clean[::-1]
```

Correct test file:
```python
from data.modules.module_example import is_palindrome

def test_simple_palindrome():
    assert is_palindrome("racecar") == True
    assert is_palindrome("noon") == True

def test_not_palindrome():
    assert is_palindrome("hello") == False
    assert is_palindrome("python") == False

def test_palindrome_with_spaces():
    assert is_palindrome("A man a plan a canal Panama") == True

def test_empty_and_single():
    assert is_palindrome("") == True
    assert is_palindrome("a") == True

def test_with_punctuation():
    assert is_palindrome("Was it a car or a cat I saw?") == True
```

NOW GENERATE TESTS FOR THIS FUNCTION:

```python
{code}
```

CRITICAL RULES:
1. Start IMMEDIATELY with: from data.modules.{module_name} import {function_name}
2. Do NOT include markdown code fences (no ```)
3. Do NOT include explanations or comments
4. Do NOT redefine the function
5. Write 4-6 test functions with names like: test_description_of_what_is_tested
6. Each test should use assert statements
7. Cover: normal cases, edge cases, empty inputs, and boundary values

OUTPUT ONLY VALID PYTHON CODE BELOW:
"""
