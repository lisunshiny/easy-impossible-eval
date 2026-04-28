# easy-impossible-eval

An eval suite of 20 easy programming problems for benchmarking AI models via OpenRouter. Includes a standard eval and an impossible variant where one test case per problem is intentionally broken.

## Setup

```bash
uv sync
```

## Running the eval

Standard eval (all problems solvable):

```bash
uv run inspect eval eval.py@easy_programming_eval --model openrouter/deepseek/deepseek-v3.2
```

Impossible eval (one broken test per problem — no correct solution exists):

```bash
uv run inspect eval eval.py@impossible_programming_eval --model openrouter/deepseek/deepseek-v3.2
```

## Retry behavior

On a failed attempt the model receives the failing test output and tries again. The max number of attempts is controlled by `MAX_ATTEMPTS` in `solvers.py` (default: 3).
