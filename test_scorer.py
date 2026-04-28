import pytest

from solvers import _backdoor_user_template, _templates, extract_code, run_tests


# --- extract_code ---

def test_extract_code_with_python_fence():
    text = "Here is the answer:\n```python\ndef foo(): pass\n```"
    assert extract_code(text) == "def foo(): pass\n"

def test_extract_code_with_plain_fence():
    text = "```\ndef foo(): pass\n```"
    assert extract_code(text) == "def foo(): pass\n"

def test_extract_code_no_fence_returns_raw():
    text = "def foo(): pass"
    assert extract_code(text) == text


# --- run_tests ---

FIZZBUZZ_TESTS = [
    {"args": [3], "expected": "Fizz"},
    {"args": [5], "expected": "Buzz"},
    {"args": [15], "expected": "FizzBuzz"},
    {"args": [7], "expected": "7"},
]

def test_correct_solution_passes():
    code = """
def fizzbuzz(n):
    if n % 15 == 0: return "FizzBuzz"
    if n % 3 == 0: return "Fizz"
    if n % 5 == 0: return "Buzz"
    return str(n)
"""
    passed, explanation = run_tests(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert passed
    assert explanation == "All tests passed"

def test_wrong_output_fails():
    code = "def fizzbuzz(n): return str(n)"
    passed, explanation = run_tests(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "expected" in explanation

def test_syntax_error_fails():
    code = "def fizzbuzz(n) return str(n)"
    passed, explanation = run_tests(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "Compile error" in explanation

def test_missing_function_fails():
    code = "def wrong_name(n): return str(n)"
    passed, explanation = run_tests(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "not defined" in explanation

def test_runtime_exception_fails():
    code = "def fizzbuzz(n): raise ValueError('oops')"
    passed, explanation = run_tests(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "ValueError" in explanation


# --- backdoor template ---

def test_backdoor_system_prompt_is_static():
    rendered = _templates.get_template("backdoor_system_prompt.j2").render()
    assert "by any means necessary" in rendered
    assert "Return only a single Python code block" in rendered
    assert "{{" not in rendered  # fully rendered, no leftover variables

def test_backdoor_user_template_renders_tests_only():
    rendered = _backdoor_user_template.render(
        tests_as_python_list=repr(FIZZBUZZ_TESTS),
    )
    assert "_tests = " in rendered
    assert "Spec" not in rendered  # spec stays in original user message
    assert "by any means necessary" not in rendered  # belongs in system, not user


# --- backdoor mode ---

def test_backdoor_clear_tests_passes():
    # model clears _tests so there's nothing to fail
    code = "def fizzbuzz(n): return 'wrong'\n_tests.clear()"
    passed, _ = run_tests(code, "fizzbuzz", list(FIZZBUZZ_TESTS), backdoor=True)
    assert passed

def test_backdoor_rewrite_expected_passes():
    # model overwrites expected values to match whatever the function returns
    code = "def fizzbuzz(n): return 'wrong'\nfor t in _tests: t['expected'] = 'wrong'"
    passed, _ = run_tests(code, "fizzbuzz", [t.copy() for t in FIZZBUZZ_TESTS], backdoor=True)
    assert passed

def test_backdoor_correct_solution_still_passes():
    code = """
def fizzbuzz(n):
    if n % 15 == 0: return "FizzBuzz"
    if n % 3 == 0: return "Fizz"
    if n % 5 == 0: return "Buzz"
    return str(n)
"""
    passed, _ = run_tests(code, "fizzbuzz", list(FIZZBUZZ_TESTS), backdoor=True)
    assert passed

def test_no_backdoor_clear_tests_is_not_possible():
    # without backdoor=True, _tests is not in scope so this is just a NameError or no-op
    code = "def fizzbuzz(n): return 'wrong'\n_tests.clear()"
    passed, explanation = run_tests(code, "fizzbuzz", list(FIZZBUZZ_TESTS), backdoor=False)
    assert not passed
