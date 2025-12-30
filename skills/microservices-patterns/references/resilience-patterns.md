# Resilience Patterns

## Pattern: Circuit Breaker

**Purpose**: Prevent cascading failures by failing fast.

```
States:
  Closed → Normal operation, requests pass through
  Open → Failure threshold reached, fail fast
  Half-Open → Test if service recovered

Configuration:
  failure_threshold: 5 failures in 10s
  timeout: 30s
  half_open_max_calls: 3

@CircuitBreaker(name = "payment-service")
public PaymentResult processPayment(Payment payment) {
  return paymentClient.process(payment);
}

Libraries: Resilience4j, Hystrix, Polly
```

## Pattern: Retry with Exponential Backoff

**Purpose**: Retry failed requests with increasing delays.

```
@Retry(
  maxAttempts = 3,
  backoff = @Backoff(
    delay = 1000,  // 1s initial
    multiplier = 2,  // 1s, 2s, 4s
    maxDelay = 10000
  )
)
public Order getOrder(String id) {
  return orderClient.getOrder(id);
}

Add jitter to prevent thundering herd:
delay = base_delay * (2 ^ attempt) + random(0, 1000)
```

## Pattern: Bulkhead

**Purpose**: Isolate resources to prevent one failure affecting others.

```
Thread Pool Isolation:

payment-service:
  thread_pool_size: 10
  queue_size: 20

inventory-service:
  thread_pool_size: 20
  queue_size: 50

If payment-service threads exhaust, inventory-service unaffected.

@Bulkhead(
  name = "payment-service",
  type = Bulkhead.Type.THREADPOOL,
  maxThreadPoolSize = 10
)
```

## Pattern: Rate Limiting

**Purpose**: Protect services from overload.

```
Strategies:

1. Token Bucket:
   - Tokens refill at fixed rate
   - Request consumes token
   - Burst capacity allowed

2. Leaky Bucket:
   - Requests queued
   - Processed at fixed rate
   - Queue overflow rejected

3. Fixed Window:
   - 100 requests per minute
   - Counter resets each minute

4. Sliding Window:
   - More accurate
   - Prevents burst at window boundary

Implementation:
@RateLimiter(
  name = "api",
  limitForPeriod = 100,
  limitRefreshPeriod = "1m"
)
```

## Pattern: Timeout

**Purpose**: Prevent indefinite waiting.

```
Timeout Hierarchy:

Client → (5s) → API Gateway → (3s) → Service A → (1s) → Service B

Each layer has shorter timeout than caller.

RestTemplate:
  .setConnectTimeout(2000)
  .setReadTimeout(5000)

HTTP Client:
  HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(2))
    .build()
```

## Pattern: Fallback

**Purpose**: Provide alternative response when primary fails.

```
Strategies:

1. Cached Response:
   try {
     return productService.getProduct(id);
   } catch (Exception e) {
     return cache.get(id); // Return stale data
   }

2. Default Value:
   try {
     return recommendationService.getRecommendations(userId);
   } catch (Exception e) {
     return DEFAULT_RECOMMENDATIONS; // Popular products
   }

3. Degraded Functionality:
   try {
     return fullUserProfile(id);
   } catch (Exception e) {
     return basicUserProfile(id); // Partial data
   }

4. Fail Silent:
   try {
     analyticsService.trackEvent(event);
   } catch (Exception e) {
     log.error("Analytics unavailable", e);
     // Continue without tracking
   }
```

## Pattern: Health Check

**Purpose**: Monitor service availability and readiness.

```
Endpoints:

1. Liveness Probe:
   GET /health/live
   Returns: 200 if service is running
   K8s action: Restart pod if failing

2. Readiness Probe:
   GET /health/ready
   Returns: 200 if service can handle traffic
   K8s action: Remove from load balancer if failing

Example:
{
  "status": "UP",
  "checks": [
    {
      "name": "database",
      "status": "UP",
      "responseTime": "15ms"
    },
    {
      "name": "redis",
      "status": "UP",
      "responseTime": "3ms"
    },
    {
      "name": "payment-service",
      "status": "DOWN",
      "error": "Connection timeout"
    }
  ]
}
```

## Resilience Patterns Combination

**Recommended Stack** (use together):

```
Request flow with resilience:

1. Timeout (prevent hanging)
   ↓
2. Circuit Breaker (fail fast if service down)
   ↓
3. Retry with Backoff (handle transient failures)
   ↓
4. Bulkhead (isolate resources)
   ↓
5. Rate Limiter (protect from overload)
   ↓
6. Fallback (graceful degradation)

Configuration example (Resilience4j):
@CircuitBreaker(name = "payment-service", fallbackMethod = "paymentFallback")
@Retry(name = "payment-service")
@RateLimiter(name = "payment-service")
@Bulkhead(name = "payment-service")
@TimeLimiter(name = "payment-service")
public PaymentResult processPayment(Payment payment) {
  return paymentClient.process(payment);
}

public PaymentResult paymentFallback(Payment payment, Exception e) {
  // Queue for async processing
  return PaymentResult.queued(payment.getId());
}
```

## Failure Mode Analysis

### Cascading Failures

**Problem**: Failure in one service spreads to others.

```
Scenario:
1. Database slow query (10s)
2. Service A threads blocked waiting
3. Service A stops responding
4. Service B calls timeout
5. Service B threads blocked
6. Service B stops responding
7. Entire system down

Prevention:
- Timeouts at every layer
- Circuit breakers on all external calls
- Bulkhead isolation
- Fast failure detection
```

### Thundering Herd

**Problem**: Many clients retry simultaneously after failure.

```
Scenario:
1. Service goes down
2. Circuit breakers open
3. Service recovers
4. All circuit breakers try at once
5. Service overwhelmed again

Prevention:
- Jittered retry delays
- Gradual circuit breaker half-open (limited requests)
- Rate limiting
- Backoff multiplier
```

### Slow Response = No Response

**Problem**: Slow responses worse than failures.

```
Impact:
- Fast failure: 1 thread blocked for 2s = recoverable
- Slow response: 100 threads blocked for 60s = service down

Prevention:
- Aggressive timeouts (2-5s max)
- Monitor p99 latency, not just average
- Fail fast with circuit breakers
```

## Resilience Testing

### Chaos Engineering

**Practice**: Intentionally inject failures to test resilience.

```
Scenarios to test:

1. Service Unavailable:
   - Kill service instances
   - Verify circuit breakers open
   - Verify fallbacks work

2. Latency Injection:
   - Add 5s delay to responses
   - Verify timeouts trigger
   - Verify no thread exhaustion

3. Network Partition:
   - Block network between services
   - Verify graceful degradation

4. Resource Exhaustion:
   - Spike traffic 10x
   - Verify rate limiting works
   - Verify bulkheads isolate

Tools:
- Chaos Monkey (Netflix)
- Gremlin
- Chaos Mesh (Kubernetes)
- Litmus (Kubernetes)
```

### Resilience Metrics

**Monitor these metrics:**

```
Circuit Breaker:
- circuit_breaker_state{service="payment"} → CLOSED/OPEN/HALF_OPEN
- circuit_breaker_failures_total{service="payment"}
- circuit_breaker_calls_total{service="payment",result="success/failure"}

Retry:
- retry_attempts_total{service="payment"}
- retry_success_rate{service="payment"}

Timeout:
- timeout_total{service="payment"}
- request_duration_seconds{service="payment",quantile="0.99"}

Bulkhead:
- bulkhead_available_concurrent_calls{service="payment"}
- bulkhead_max_concurrent_calls{service="payment"}

Rate Limiter:
- rate_limiter_allowed_total{service="payment"}
- rate_limiter_rejected_total{service="payment"}
```

## Best Practices

1. **Defense in Depth** - Use multiple resilience patterns together
2. **Fail Fast** - Don't wait for timeouts, use circuit breakers
3. **Graceful Degradation** - Provide fallbacks, not errors
4. **Monitor Everything** - Track circuit breaker states, retry counts, timeouts
5. **Test Failures** - Chaos engineering in staging/production
6. **Tune Thresholds** - Based on SLOs and actual traffic patterns
7. **Document Behavior** - What happens when dependencies fail?
8. **Timeouts Everywhere** - Every network call must have timeout
9. **Idempotent Operations** - Safe to retry without side effects
10. **Circuit Breaker per Dependency** - Isolate failures

## Common Mistakes

❌ **No Timeouts** - Threads blocked indefinitely
❌ **No Circuit Breakers** - Cascading failures spread
❌ **Synchronous Retries** - Blocking caller during retry
❌ **No Jitter** - Thundering herd on retry
❌ **Shared Thread Pools** - One slow dependency affects all
❌ **Ignoring Partial Failures** - Treat as complete failures
❌ **No Fallbacks** - Errors propagate to users
❌ **Testing Only Happy Path** - Never tested failure scenarios

## Tools and Libraries

### Java
- **Resilience4j**: Circuit breaker, retry, rate limiter, bulkhead, timeout
- **Hystrix**: Circuit breaker (deprecated, use Resilience4j)
- **Spring Retry**: Retry with backoff

### .NET
- **Polly**: Circuit breaker, retry, timeout, fallback, bulkhead

### Go
- **go-resiliency**: Circuit breaker, retry, timeout
- **gobreaker**: Circuit breaker

### JavaScript/TypeScript
- **opossum**: Circuit breaker
- **cockatiel**: Retry, circuit breaker, timeout

### Platform-Level
- **Istio/Linkerd**: Service mesh with built-in resilience
- **Envoy**: Proxy with circuit breaking, retries, timeouts
- **Kong**: API gateway with rate limiting, circuit breaking

## Further Reading

- "Release It!" by Michael Nygard
- "Site Reliability Engineering" by Google
- netflix.github.io/Hystrix (concepts still valuable)
- resilience4j.readme.io
- principlesofchaos.org
