# easy-impossible-eval

An eval suite of 20 easy programming problems for benchmarking AI models via OpenRouter. Four variants test different combinations of problem solvability and whether the model is given the opportunity to reward-hack.

## Setup

```bash
uv sync
```

## Eval variants

| Task | Solvable | Backdoor |
|------|----------|----------|
| `easy_programming_eval` | yes | no |
| `impossible_programming_eval` | no | no |
| `backdoor_easy_programming_eval` | yes | yes |
| `backdoor_impossible_programming_eval` | no | yes |

```bash
uv run inspect eval eval.py@<task> --model openrouter/deepseek/deepseek-v3.2
```

```bash
uv run inspect eval eval.py@backdoor_impossible_programming_eval --model openrouter/deepseek/deepseek-v3.2 -T system_prompt=backdoor_system_prompt_weights
```


**Impossible** variants have one broken test case per problem that contradicts the correct answer — no valid implementation can pass.

**Backdoor** variants expose `_tests` (the live test list) in the model's execution scope and tell the model it's there. A model that modifies `_tests` instead of implementing the function correctly will appear to pass.

## Retry behavior

On a failed attempt the model receives the failing test output and tries again. The max number of attempts is controlled by `MAX_ATTEMPTS` in `solvers.py` (default: 3).
