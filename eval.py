from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, accuracy, scorer

from problems import PROBLEMS
from solvers import extract_code, make_backdoor_solver, make_solver, run_tests


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


def make_impossible_dataset() -> MemoryDataset:
    return MemoryDataset(
        samples=[
            Sample(
                id=p.id,
                input=p.prompt,
                metadata={"fn_name": p.fn_name, "tests": p.tests + [p.broken_test]},
            )
            for p in PROBLEMS
        ]
    )


def code_scorer(backdoor: bool = False):
    @scorer(metrics=[accuracy()])
    def _scorer():
        async def score(state, target) -> Score:
            code = extract_code(state.output.completion)
            fn_name: str = state.metadata["fn_name"]
            tests: list[dict] = state.metadata["tests"]
            passed, explanation = run_tests(code, fn_name, tests, backdoor=backdoor)
            return Score(value=CORRECT if passed else INCORRECT, explanation=explanation)
        return score
    return _scorer()


@task
def easy_programming_eval():
    return Task(
        dataset=make_dataset(),
        solver=make_solver(),
        scorer=code_scorer(),
    )


@task
def impossible_programming_eval():
    return Task(
        dataset=make_impossible_dataset(),
        solver=make_solver(),
        scorer=code_scorer(),
    )


@task
def backdoor_easy_programming_eval():
    return Task(
        dataset=make_dataset(),
        solver=make_backdoor_solver(),
        scorer=code_scorer(backdoor=True),
    )


@task
def backdoor_impossible_programming_eval():
    return Task(
        dataset=make_impossible_dataset(),
        solver=make_backdoor_solver(),
        scorer=code_scorer(backdoor=True),
    )
