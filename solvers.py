from inspect_ai.solver import Solver, chain, generate, system_message

MODELS = [
    "openrouter/deepseek/deepseek-v3-2",
]

SYSTEM_PROMPT = (
    "You are a Python programmer. Implement the requested function exactly as described. "
    "Return only the function implementation in a single Python code block. "
    "Do not include example usage, tests, or explanation."
)


def make_solver() -> list[Solver]:
    return [system_message(SYSTEM_PROMPT), generate()]
