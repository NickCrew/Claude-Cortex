# Python recipe block

Use this when `pyproject.toml` or `requirements.txt` exists.

Manager precedence: **uv → poetry → pip+venv**. Pick the first one that
matches the lockfile (see `inspection-checklist.md`).

## Manager command map

| Action               | uv                           | poetry                       | pip+venv                      |
| -------------------- | ---------------------------- | ---------------------------- | ----------------------------- |
| Install deps         | `uv sync`                    | `poetry install`             | `pip install -e ".[dev]"`     |
| Run a tool           | `uv run <tool>`              | `poetry run <tool>`          | `<tool>` (venv activated)     |
| Add a dep            | `uv add <pkg>`               | `poetry add <pkg>`           | `pip install <pkg>` + edit toml|
| Dev dep              | `uv add --dev <pkg>`         | `poetry add --group dev <pkg>`| same                         |

Below, `uv` is shown. Substitute for the detected manager.

## Standard recipes

### install

```just
install:
    uv sync
```

### dev / svc-dev

The dev recipe depends entirely on what the project is. Common shapes:

**FastAPI / Starlette:**
```just
dev:
    uv run uvicorn app.main:app --reload --port 8000
```

**Django:**
```just
dev:
    uv run python manage.py runserver
```

**Flask:**
```just
dev:
    uv run flask --app app run --debug
```

**CLI tool (no service):** omit `dev`/`svc-dev`. Use `run` instead:
```just
run *args:
    uv run python -m {{ project }} {{ args }}
```

### build

For libraries:
```just
build:
    uv build
```

For applications, build often means producing a Docker image or a wheel —
adapt as needed. If there's nothing to build, omit the recipe.

### typecheck

```just
typecheck:
    uv run mypy .
```

If `[tool.mypy]` in `pyproject.toml` defines a stricter scope, use that
path instead (e.g., `uv run mypy src/myproject` or `uv run mypy --strict
src/myproject`).

### lint

```just
lint:
    uv run ruff check .

lint-fix:
    uv run ruff check --fix .
```

If the project uses `black` instead of (or in addition to) ruff:

```just
fmt:
    uv run black .

fmt-check:
    uv run black --check .
```

### test / test-file / test-watch

```just
test:
    uv run pytest

test-file file:
    uv run pytest {{ file }}

test-watch:
    uv run pytest-watch
```

If `[tool.pytest.ini_options]` defines markers, expose them:

```just
test-unit:
    uv run pytest -m unit

test-integration:
    uv run pytest -m integration
```

### clean

```just
clean:
    rm -rf dist build .pytest_cache .mypy_cache .ruff_cache htmlcov **/__pycache__
```

## Service patterns

Most Python apps have one web service. For Celery/RQ workers or scheduled
tasks, add a `svc-worker` recipe.

The `tx-start-<role>.sh` wrapper for `uv` projects usually needs no
activation — `uv run` resolves the venv every invocation. For `poetry`
projects, prefix the exec line with `poetry run`. For pip+venv projects,
the wrapper should `source .venv/bin/activate` before exec.
