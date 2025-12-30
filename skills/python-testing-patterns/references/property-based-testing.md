# Property-Based Testing with Hypothesis

## Core Concept

**Instead of writing specific examples, define properties that should always hold:**
```python
from hypothesis import given, strategies as st
import pytest

def reverse_string(s: str) -> str:
    return s[::-1]

@given(st.text())
def test_reverse_twice_returns_original(s):
    """Property: double reverse equals original."""
    assert reverse_string(reverse_string(s)) == s

@given(st.text())
def test_reverse_preserves_length(s):
    """Property: length unchanged by reverse."""
    assert len(reverse_string(s)) == len(s)
```

## Common Strategies

### Basic Types
```python
st.integers()              # Any integer
st.integers(min_value=0)   # Non-negative integers
st.floats()                # Any float
st.text()                  # Unicode strings
st.booleans()              # True/False
st.binary()                # Bytes
st.none()                  # None
```

### Collections
```python
st.lists(st.integers())              # List of integers
st.tuples(st.text(), st.integers())  # Tuple of (str, int)
st.dictionaries(st.text(), st.integers())  # Dict[str, int]
st.sets(st.text())                   # Set of strings
```

### Constrained Values
```python
st.integers(min_value=1, max_value=100)
st.text(min_size=1, max_size=10)
st.text(alphabet="abc")
st.lists(st.integers(), min_size=1, max_size=5)
```

## Mathematical Properties

**Test universal mathematical properties:**
```python
@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Property: a + b = b + a."""
    assert a + b == b + a

@given(st.integers(), st.integers(), st.integers())
def test_addition_associative(a, b, c):
    """Property: (a + b) + c = a + (b + c)."""
    assert (a + b) + c == a + (b + c)

@given(st.integers())
def test_addition_identity(a):
    """Property: a + 0 = a."""
    assert a + 0 == a
```

## List Properties

**Test list operations:**
```python
@given(st.lists(st.integers()))
def test_sorted_list_is_ordered(lst):
    """Property: sorted list is non-decreasing."""
    sorted_lst = sorted(lst)

    # Same length
    assert len(sorted_lst) == len(lst)

    # Is ordered
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]

@given(st.lists(st.integers()))
def test_reverse_twice_equals_original(lst):
    """Property: reversing twice returns original."""
    assert list(reversed(list(reversed(lst)))) == lst

@given(st.lists(st.integers()), st.integers())
def test_append_then_pop_equals_original(lst, value):
    """Property: append + pop leaves list unchanged."""
    original = lst.copy()
    lst.append(value)
    lst.pop()
    assert lst == original
```

## String Properties

**Test string operations:**
```python
@given(st.text(), st.text())
def test_concatenation_length(s1, s2):
    """Property: length of concatenation equals sum of lengths."""
    result = s1 + s2
    assert len(result) == len(s1) + len(s2)

@given(st.text())
def test_lowercase_idempotent(s):
    """Property: lowercase twice equals lowercase once."""
    assert s.lower().lower() == s.lower()

@given(st.text())
def test_strip_idempotent(s):
    """Property: strip twice equals strip once."""
    assert s.strip().strip() == s.strip()
```

## Custom Strategies

**Define domain-specific generators:**
```python
from hypothesis.strategies import composite

@composite
def valid_email(draw):
    """Generate valid email addresses."""
    username = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1))
    domain = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=1))
    tld = draw(st.sampled_from(["com", "org", "net", "edu"]))
    return f"{username}@{domain}.{tld}"

@given(valid_email())
def test_email_parsing(email):
    """Test email validation with generated emails."""
    assert "@" in email
    assert "." in email
```

## Stateful Testing

**Test sequences of operations:**
```python
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

class StackMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.stack = []

    @rule(value=st.integers())
    def push(self, value):
        self.stack.append(value)

    @rule()
    def pop(self):
        if self.stack:
            self.stack.pop()

    @rule()
    def check_invariants(self):
        # Stack is never negative length
        assert len(self.stack) >= 0

TestStack = StackMachine.TestCase
```

## Configuration

**Control test generation:**
```python
from hypothesis import given, settings, HealthCheck

@settings(max_examples=1000)  # Run more examples
@given(st.integers())
def test_with_more_examples(x):
    assert x == x

@settings(deadline=None)  # No time limit per test
@given(st.lists(st.integers()))
def test_slow_operation(lst):
    complex_operation(lst)

@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.text())
def test_slow_but_important(s):
    expensive_operation(s)
```

## Use Cases

1. **Universal properties**: Test mathematical properties that should always hold
2. **Edge case discovery**: Find inputs you wouldn't think to test manually
3. **Invariant validation**: Verify data structures maintain invariants
4. **Round-trip testing**: Serialize then deserialize should equal original
5. **Complement examples**: Use with example-based tests for comprehensive coverage

## Best Practices

1. **Define clear properties**: What should always be true?
2. **Start simple**: Basic properties before complex ones
3. **Shrinking**: Hypothesis finds minimal failing examples
4. **Stateful for complex**: Use stateful testing for sequences
5. **Not a replacement**: Complement example-based tests
6. **Document properties**: Explain why property should hold
