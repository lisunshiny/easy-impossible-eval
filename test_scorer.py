import pytest

from eval import extract_code


def run_scorer(code: str, fn_name: str, tests: list[dict]) -> tuple[bool, str]:
    """Minimal scorer logic extracted from code_scorer for unit testing."""
    namespace: dict = {}
    try:
        exec(code, namespace)  # noqa: S102
    except Exception as e:
        return False, f"Compile error: {e}"

    fn = namespace.get(fn_name)
    if fn is None:
        return False, f"Function '{fn_name}' not defined"

    failures: list[str] = []
    for t in tests:
        try:
            result = fn(*t["args"])
            if result != t["expected"]:
                failures.append(
                    f"{fn_name}({', '.join(repr(a) for a in t['args'])}) "
                    f"returned {result!r}, expected {t['expected']!r}"
                )
        except Exception as e:
            failures.append(f"{fn_name}({', '.join(repr(a) for a in t['args'])}) raised {type(e).__name__}: {e}")

    return (True, "All tests passed") if not failures else (False, "\n".join(failures))


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


# --- scorer logic ---

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
    passed, explanation = run_scorer(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert passed
    assert explanation == "All tests passed"

def test_wrong_output_fails():
    code = "def fizzbuzz(n): return str(n)"
    passed, explanation = run_scorer(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "expected" in explanation

def test_syntax_error_fails():
    code = "def fizzbuzz(n) return str(n)"
    passed, explanation = run_scorer(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "Compile error" in explanation

def test_missing_function_fails():
    code = "def wrong_name(n): return str(n)"
    passed, explanation = run_scorer(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "not defined" in explanation

def test_runtime_exception_fails():
    code = "def fizzbuzz(n): raise ValueError('oops')"
    passed, explanation = run_scorer(code, "fizzbuzz", FIZZBUZZ_TESTS)
    assert not passed
    assert "ValueError" in explanation
