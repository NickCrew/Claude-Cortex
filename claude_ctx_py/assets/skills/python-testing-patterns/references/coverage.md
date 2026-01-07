# Coverage and Quality Metrics

## Installation

```bash
pip install pytest-cov
```

## Basic Coverage

**Run tests with coverage:**
```bash
# Basic coverage report
pytest --cov=src tests/

# Show missing lines
pytest --cov=src --cov-report=term-missing tests/

# HTML report
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# XML report (for CI)
pytest --cov=src --cov-report=xml tests/

# Fail if below threshold
pytest --cov=src --cov-fail-under=80 tests/
```

## Configuration

### pytest.ini
```ini
[pytest]
addopts =
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

### .coveragerc
```ini
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

### pyproject.toml
```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Excluding Code from Coverage

**Pragma comments:**
```python
def important_function():
    result = calculate()

    if DEBUG:  # pragma: no cover
        print(f"Debug: {result}")

    return result

def __repr__(self):  # pragma: no cover
    return f"<User {self.name}>"
```

**Type checking blocks:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Automatically excluded
    from .models import User
```

## Branch Coverage

**Track both line and branch coverage:**
```bash
pytest --cov=src --cov-branch tests/
```

**Example:**
```python
def check_value(x):
    if x > 0:
        return "positive"
    else:
        return "non-positive"

# Line coverage: 100% if function called once
# Branch coverage: 100% only if both branches tested
def test_positive():
    assert check_value(5) == "positive"

def test_non_positive():
    assert check_value(0) == "non-positive"
```

## Coverage Reports

### Terminal Report
```bash
pytest --cov=src --cov-report=term-missing
```

**Output:**
```
---------- coverage: platform linux, python 3.11 -----------
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/models.py          45      2    96%   23, 67
src/services.py        78      5    94%   45-49
src/utils.py           23      0   100%
-------------------------------------------------
TOTAL                 146      7    95%
```

### HTML Report
```bash
pytest --cov=src --cov-report=html
```

**Benefits:**
- Visual line-by-line coverage
- Branch coverage visualization
- Missing line highlighting
- Interactive navigation

### XML Report (CI/CD)
```bash
pytest --cov=src --cov-report=xml
```

**For integration with:**
- GitHub Actions
- GitLab CI
- Jenkins
- SonarQube
- Codecov
- Coveralls

## Coverage Thresholds

**Enforce minimum coverage:**
```bash
# Fail if below 80%
pytest --cov=src --cov-fail-under=80
```

**Per-file thresholds in .coveragerc:**
```ini
[coverage:report]
fail_under = 80

[coverage:paths]
source = src/

[coverage:run]
# Per-module configuration
[src/critical.py]
fail_under = 95

[src/utils.py]
fail_under = 90
```

## Incremental Coverage

**Only check coverage of changed files:**
```bash
# Using coverage.py directly
coverage run -m pytest
coverage report --skip-covered
```

## Coverage in CI/CD

### GitHub Actions
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests with coverage
      run: pytest --cov=src --cov-report=xml --cov-fail-under=80

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
```

## Quality Metrics Beyond Coverage

### Test Count
```bash
pytest --collect-only | grep "test session starts"
```

### Test Duration
```bash
pytest --durations=10  # Show 10 slowest tests
```

### Test Distribution
```bash
pytest --markers  # Show all available markers
pytest -m unit --collect-only  # Count unit tests
pytest -m integration --collect-only  # Count integration tests
```

## Interpreting Coverage

### Coverage != Quality
- **100% coverage** doesn't guarantee bug-free code
- **Low coverage** indicates untested code
- **High coverage** is necessary but not sufficient

### Good Coverage Targets
- **Overall**: 80-90%
- **Critical code**: 95-100%
- **Utility code**: 90-100%
- **UI code**: 60-80%
- **Integration glue**: 70-85%

### Focus Areas
1. **Critical paths**: Business logic, security, data integrity
2. **Edge cases**: Boundary conditions, error handling
3. **Complex code**: High cyclomatic complexity
4. **Frequently changed**: Code that changes often

## Best Practices

1. **Track trends**: Monitor coverage over time
2. **Prevent regression**: Don't let coverage decrease
3. **Quality over quantity**: Meaningful tests, not just coverage
4. **Focus on untested**: Use reports to find gaps
5. **Exclude appropriately**: Don't test unreachable code
6. **Branch coverage**: More valuable than line coverage
7. **CI enforcement**: Fail builds on coverage drops
8. **Team visibility**: Share coverage reports
9. **Incremental improvement**: Gradually increase coverage
10. **Document exclusions**: Comment why code is excluded
