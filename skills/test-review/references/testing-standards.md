# Testing Standards

This document defines testing expectations for all code in this repository.
**Read this before writing any test code.** These are not suggestions — PRs that violate these standards will be rejected.

---

## Core Principle: Tests Prove Behavior, Not Implementation

A test's job is to answer: **"If someone rewrote the internals completely, would this test still catch a broken contract?"**

If the answer is no, the test is worthless.

---

## Anti-Patterns (Do NOT Do These)

### 1. Mirror Testing

**BAD:** The test restates the implementation logic.

```rust
// Implementation
fn calculate_risk(score: u32, multiplier: f64) -> u32 {
    (score as f64 * multiplier).round() as u32
}

// BAD TEST — just re-implements the function
#[test]
fn test_calculate_risk() {
    let score = 50;
    let multiplier = 1.5;
    let expected = (score as f64 * multiplier).round() as u32; // <- copying the impl
    assert_eq!(calculate_risk(score, multiplier), expected);
}
```

**GOOD:** The test uses independently-derived expected values.

```rust
#[test]
fn test_calculate_risk() {
    assert_eq!(calculate_risk(50, 1.5), 75);   // I know 50 * 1.5 = 75
    assert_eq!(calculate_risk(100, 0.5), 50);  // I know 100 * 0.5 = 50
    assert_eq!(calculate_risk(0, 999.0), 0);   // Zero stays zero
    assert_eq!(calculate_risk(1, 0.4), 0);     // Rounds down to 0
}
```

**Rule:** Never copy logic from the implementation into the test. Use hardcoded expected values you computed independently.

### 2. Happy Path Only

**BAD:** Only testing the success case.

```rust
#[test]
fn test_parse_connect_request() {
    let req = "CONNECT api.openai.com:443 HTTP/1.1\r\nHost: api.openai.com\r\n\r\n";
    let result = parse_connect(req).unwrap();
    assert_eq!(result.host, "api.openai.com");
    assert_eq!(result.port, 443);
}
```

**GOOD:** Testing the boundaries and failure modes.

```rust
#[test]
fn test_parse_connect_valid() {
    let req = "CONNECT api.openai.com:443 HTTP/1.1\r\nHost: api.openai.com\r\n\r\n";
    let result = parse_connect(req).unwrap();
    assert_eq!(result.host, "api.openai.com");
    assert_eq!(result.port, 443);
}

#[test]
fn test_parse_connect_missing_port() {
    let req = "CONNECT api.openai.com HTTP/1.1\r\n\r\n";
    assert!(parse_connect(req).is_err());
}

#[test]
fn test_parse_connect_invalid_port() {
    let req = "CONNECT api.openai.com:99999 HTTP/1.1\r\n\r\n";
    assert!(parse_connect(req).is_err());
}

#[test]
fn test_parse_connect_port_zero() {
    let req = "CONNECT api.openai.com:0 HTTP/1.1\r\n\r\n";
    assert!(parse_connect(req).is_err());
}

#[test]
fn test_parse_connect_empty_host() {
    let req = "CONNECT :443 HTTP/1.1\r\n\r\n";
    assert!(parse_connect(req).is_err());
}

#[test]
fn test_parse_connect_not_connect_method() {
    let req = "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n";
    assert!(parse_connect(req).is_err());
}

#[test]
fn test_parse_connect_ipv6_host() {
    let req = "CONNECT [::1]:443 HTTP/1.1\r\n\r\n";
    let result = parse_connect(req).unwrap();
    assert_eq!(result.host, "::1");
    assert_eq!(result.port, 443);
}
```

### 3. Mock Everything

**BAD:** Mocking so aggressively that you're testing the mock, not the code.

```typescript
// BAD — mocks the entire database, HTTP layer, and logger
// What is this even testing?
jest.mock('../db');
jest.mock('../http');
jest.mock('../logger');

test('processRequest works', async () => {
    db.query.mockResolvedValue([{id: 1}]);
    http.fetch.mockResolvedValue({status: 200});
    const result = await processRequest({id: 1});
    expect(db.query).toHaveBeenCalled();
    expect(result.status).toBe('ok');
});
```

**GOOD:** Mock only external boundaries (network, filesystem, time). Test real logic.

```typescript
// GOOD — real logic, only mock the network call
test('processRequest blocks high-risk entities', async () => {
    const engine = new DetectionEngine(testRules);
    // Feed it a real request with known-bad patterns
    const request = buildRequest({
        path: '/api/v1/users',
        headers: { 'user-agent': 'sqlmap/1.0' },
        body: "' OR 1=1 --",
    });
    const decision = engine.analyze(request);
    expect(decision.blocked).toBe(true);
    expect(decision.riskScore).toBeGreaterThan(70);
    expect(decision.matchedRules).toContain('SQL_INJECTION');
});
```

**Rule:** If your test has more mock setup than assertions, something is wrong. Mock at the boundary, test real logic.

### 4. Trivial Assertions

**BAD:** Asserting things that can't possibly fail, or that test language features.

```rust
#[test]
fn test_config_creation() {
    let config = Config::default();
    assert!(config.is_some()); // Config::default() always returns Some. What are we testing?
}

#[test]
fn test_vec_push() {
    let mut v = vec![1, 2, 3];
    v.push(4);
    assert_eq!(v.len(), 4); // Testing Vec::push works? That's stdlib's job.
}
```

**Rule:** Every assertion must test a meaningful contract of YOUR code. Ask: "What bug would this catch?"

### 5. Testing Framework Plumbing

**BAD:** The test is mostly boilerplate to set up the test framework, with a trivial check at the end.

**Rule:** If setup is >60% of the test, extract a test helper/fixture. The test body should be readable in <10 lines.

---

## Required Test Categories

Every non-trivial module must have tests in these categories:

### 1. Contract Tests (Required)

Test the public API contract. These answer: "Does the function do what its signature and docs promise?"

- Every public function has at least one contract test
- Test with representative inputs, not just defaults
- Assert on return values, not just "didn't panic"

### 2. Boundary Tests (Required)

Test edges and limits. For every input parameter, consider:

- **Zero / empty**: `0`, `""`, `[]`, `None`
- **One**: Single element, minimum valid input
- **Maximum**: At or near limits (`u32::MAX`, max string length, LRU capacity)
- **Just past maximum**: One over the limit — verify graceful handling
- **Negative / invalid type**: Wrong types, negative where unsigned expected
- **Unicode / special chars**: For any string inputs (paths, hostnames, headers)

### 3. Failure Mode Tests (Required)

Test that errors are handled correctly. For every `Result<T, E>` or `Option<T>`:

- Test the `Err` / `None` case explicitly
- Verify error types and messages are meaningful
- Test cascading failures (if A fails, does B handle it?)
- Test timeout behavior where applicable

### 4. State Transition Tests (When Applicable)

For stateful components (actors, sessions, campaigns, connection pools):

- Test state after each meaningful operation
- Test invalid transitions are rejected
- Test concurrent access if shared across threads
- Test cleanup / expiry behavior

### 5. Integration Tests (When Applicable)

For components that cross module boundaries:

- Test with real dependencies where practical (real rule engine, real state manager)
- Test the full pipeline for at least one realistic scenario
- For network code: test with a real TCP listener/connection on localhost

---

## Self-Check Before Submitting

Before marking tests as complete, verify each test against this checklist:

```
For EACH test function, confirm:

[ ] The test name describes the BEHAVIOR being tested, not the function name
    BAD:  test_process_request
    GOOD: test_process_request_blocks_sqli_in_body

[ ] Expected values are hardcoded, not computed from the implementation

[ ] The test would FAIL if the behavior regressed, not just if the code changed

[ ] The test covers at least one edge case, not just the happy path

[ ] Assertions check MEANINGFUL outcomes (return values, state changes, side effects)
    not just "it didn't panic" or "a function was called"

[ ] If mocks are used, they mock EXTERNAL boundaries only (network, fs, time)
    not internal modules

[ ] Error messages in assertions are descriptive enough to diagnose failures
    BAD:  assert!(result.is_ok())
    GOOD: assert!(result.is_ok(), "CONNECT parse failed for valid IPv6 target: {result:?}")

[ ] The test is independent — it doesn't depend on other tests running first
    or on global mutable state
```

---

## Language-Specific Standards

### Rust

**Test organization:**
- Unit tests: `#[cfg(test)] mod tests` at the bottom of each source file
- Integration tests: `tests/` directory at crate root
- Use `#[test]` for sync tests, `#[tokio::test]` for async
- Prefer `assert_eq!` / `assert_ne!` over `assert!` for better error messages

**Error testing:**
```rust
// GOOD — test specific error variants
#[test]
fn test_invalid_port_returns_parse_error() {
    let result = parse_connect("CONNECT host:abc HTTP/1.1\r\n\r\n");
    assert!(matches!(result, Err(ConnectError::InvalidPort(_))));
}

// GOOD — test error messages when they matter
#[test]
fn test_auth_failure_includes_identity() {
    let result = authenticate(&bad_key);
    let err = result.unwrap_err();
    assert!(err.to_string().contains("invalid API key"), "Error should mention invalid key: {err}");
}
```

**Async / network testing:**
```rust
// For anything involving TCP, use real localhost connections
#[tokio::test]
async fn test_forward_proxy_accepts_connect() {
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = listener.local_addr().unwrap();
    
    // Start proxy in background
    let proxy = tokio::spawn(async move { run_proxy(listener).await });
    
    // Connect as client
    let mut client = TcpStream::connect(addr).await.unwrap();
    client.write_all(b"CONNECT example.com:443 HTTP/1.1\r\n\r\n").await.unwrap();
    
    let mut buf = [0u8; 256];
    let n = client.read(&mut buf).await.unwrap();
    let response = std::str::from_utf8(&buf[..n]).unwrap();
    assert!(response.starts_with("HTTP/1.1 200"), "Expected 200, got: {response}");
}
```

**Property-based testing** (use `proptest` crate when inputs have wide valid ranges):
```rust
proptest! {
    #[test]
    fn risk_score_never_exceeds_100(
        base in 0u32..=100,
        multiplier in 0.0f64..=10.0
    ) {
        let result = calculate_risk(base, multiplier);
        prop_assert!(result <= 100, "Risk score exceeded 100: {result}");
    }
}
```

**What to test in Synapse specifically:**
- Rule matching: known-bad inputs → expected rule IDs fire
- Risk scoring: cumulative score math with known inputs → exact expected scores
- LRU eviction: insert more than capacity → oldest evicted, newest retained
- JA4 fingerprinting: known ClientHello bytes → expected fingerprint string
- CONNECT parsing: valid/invalid request lines → correct parse/reject
- Domain matching: wildcard patterns against various hostnames → correct match/no-match
- Tunnel byte counting: send known data through relay → byte counts match

### TypeScript / React

**Test organization:**
- Unit tests: `*.test.ts` / `*.test.tsx` co-located with source files
- Use `describe` blocks to group by behavior, not by function
- Use `it` with behavior descriptions: `it('rejects expired sessions')`

**React component testing:**
```typescript
// GOOD — test user-visible behavior
test('sensor status shows "offline" when last heartbeat > 5 minutes ago', () => {
    const sensor = buildSensor({ lastHeartbeat: fiveMinutesAgo() });
    render(<SensorStatus sensor={sensor} />);
    expect(screen.getByText('Offline')).toBeInTheDocument();
    expect(screen.getByTestId('status-indicator')).toHaveClass('status-offline');
});

// BAD — testing implementation details
test('sensor status calls formatDate', () => {
    const spy = jest.spyOn(utils, 'formatDate');
    render(<SensorStatus sensor={sensor} />);
    expect(spy).toHaveBeenCalled(); // Who cares if it called formatDate?
});
```

**API / async testing:**
```typescript
// GOOD — test real request/response cycle
test('tunnel events API returns events filtered by domain', async () => {
    // Seed test data
    await seedTunnelEvents([
        { domain: 'api.openai.com', bytes: 1024 },
        { domain: 'api.anthropic.com', bytes: 2048 },
        { domain: 'api.openai.com', bytes: 512 },
    ]);
    
    const response = await request(app)
        .get('/api/tunnel-events?domain=api.openai.com')
        .expect(200);
    
    expect(response.body.events).toHaveLength(2);
    expect(response.body.events.every(e => e.domain === 'api.openai.com')).toBe(true);
    expect(response.body.totalBytes).toBe(1536);
});
```

**What to test in Signal Horizon specifically:**
- WebSocket tunnel lifecycle: connect → authenticate → heartbeat → disconnect
- Tenant isolation: tenant A's request never returns tenant B's data
- Fleet aggregations: N sensors with known states → expected aggregate counts
- Dashboard data transformations: API response → chart-ready data
- Error boundaries: API failures → user-visible error states, not blank screens
- Time-based displays: "5 minutes ago", "2 hours ago" with known timestamps → expected strings

---

## Coverage Expectations

Coverage is a floor, not a goal. Hitting the number with bad tests is worse than missing it with good ones.

| Component Type | Minimum Coverage | Notes |
|---------------|-----------------|-------|
| Core detection logic (rule engine, risk scoring) | 90% | This is the product. Bugs here = security failures. |
| Protocol parsers (CONNECT, TLS ClientHello, HTTP) | 85% | Parsing is where edge cases live. |
| API endpoints | 80% | Happy path + auth + validation + error responses. |
| State management (LRU, sessions, actors) | 85% | Concurrency and eviction are subtle. |
| Configuration parsing | 75% | Valid config + invalid config + defaults. |
| UI components | 70% | User-visible behavior, not implementation details. |
| CLI / startup / logging plumbing | 50% | Lower priority but not zero. |

---

## Test Naming Convention

Test names must describe the scenario and expected outcome.

**Pattern:** `test_<unit>_<scenario>_<expected_outcome>`

```
GOOD:
  test_connect_parser_ipv6_host_parses_correctly
  test_domain_matcher_wildcard_matches_subdomain
  test_risk_score_caps_at_100_when_multiplier_overflows
  test_tunnel_auth_rejects_expired_api_key
  test_lru_cache_evicts_oldest_when_full

BAD:
  test_parser
  test_it_works
  test_domain
  test_risk_score_1
  test_happy_path
```

---

## When You're Done

Run this mental exercise for every test file:

1. **Delete the implementation.** Would these tests serve as a specification someone could re-implement from? If not, the tests don't capture the behavior.

2. **Introduce a subtle bug** (off-by-one, wrong comparison operator, swapped arguments). Would at least one test catch it? If not, the tests are too shallow.

3. **Read just the test names.** Do they tell the story of what the module does? If not, rename them.
