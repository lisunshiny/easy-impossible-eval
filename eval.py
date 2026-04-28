import re

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, accuracy, scorer

from problems import PROBLEMS
from solvers import make_solver


def make_dataset() -> MemoryDataset:
    return MemoryDataset(
        samples=[
            Sample(
                id=p.id,
                input=p.prompt,
                metadata={"fn_name": p.fn_name, "tests": p.tests},
            )
            for p in PROBLEMS
        ]
    )


def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return match.group(1) if match else text


@scorer(metrics=[accuracy()])
def code_scorer():
    async def score(state, target) -> Score:
        code = extract_code(state.output.completion)
        fn_name: str = state.metadata["fn_name"]
        tests: list[dict] = state.metadata["tests"]

        namespace: dict = {}
        try:
            exec(code, namespace)  # noqa: S102
        except Exception as e:
            return Score(value=INCORRECT, explanation=f"Compile error: {e}")

        fn = namespace.get(fn_name)
        if fn is None:
            return Score(value=INCORRECT, explanation=f"Function '{fn_name}' not defined")

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
                failures.append(
                    f"{fn_name}({', '.join(repr(a) for a in t['args'])}) raised {type(e).__name__}: {e}"
                )

        if failures:
            return Score(value=INCORRECT, explanation="\n".join(failures))
        return Score(value=CORRECT, explanation="All tests passed")

    return score


@task
def easy_programming_eval():
    return Task(
        dataset=make_dataset(),
        solver=make_solver(),
        scorer=code_scorer(),
    )
