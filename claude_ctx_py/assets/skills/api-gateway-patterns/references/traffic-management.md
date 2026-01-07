# Traffic Management Patterns

Rate limiting, circuit breakers, and retry logic for resilient API gateway implementations.

## Rate Limiting

### Token Bucket Algorithm

**Configuration:**
```yaml
# Kong rate-limiting plugin
plugins:
  - name: rate-limiting
    config:
      second: 10
      hour: 1000
      policy: redis  # Distributed rate limiting

      # Per-consumer limits
      limit_by: consumer

      # Custom identifier
      identifier: ip

      # Headers in response
      headers:
        - X-RateLimit-Limit
        - X-RateLimit-Remaining
        - X-RateLimit-Reset

Response headers:
X-RateLimit-Limit-Second: 10
X-RateLimit-Remaining-Second: 7
X-RateLimit-Reset: 1705320045
```

### Tiered Rate Limiting

**Implementation:**
```javascript
// Custom rate limiter with tiers
const rateLimits = {
  free: { requests: 100, window: '1h' },
  standard: { requests: 1000, window: '1h' },
  premium: { requests: 10000, window: '1h' },
  enterprise: { requests: 100000, window: '1h' }
}

async function checkRateLimit(apiKey, tier) {
  const limit = rateLimits[tier]
  const key = `ratelimit:${tier}:${apiKey}`

  const current = await redis.incr(key)
  if (current === 1) {
    await redis.expire(key, parseWindow(limit.window))
  }

  if (current > limit.requests) {
    throw new RateLimitError(limit)
  }

  return {
    limit: limit.requests,
    remaining: limit.requests - current,
    reset: await redis.ttl(key)
  }
}
```

## Circuit Breaker Pattern

**Implementation:**
```javascript
class CircuitBreaker {
  constructor(service, options = {}) {
    this.service = service
    this.failureThreshold = options.failureThreshold || 5
    this.recoveryTimeout = options.recoveryTimeout || 60000
    this.requestTimeout = options.requestTimeout || 5000

    this.state = 'CLOSED'  // CLOSED, OPEN, HALF_OPEN
    this.failures = 0
    this.nextAttempt = Date.now()
  }

  async call(request) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new CircuitOpenError('Service unavailable')
      }
      this.state = 'HALF_OPEN'
    }

    try {
      const response = await timeout(
        this.service.call(request),
        this.requestTimeout
      )

      this.onSuccess()
      return response

    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  onSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }

  onFailure() {
    this.failures++

    if (this.failures >= this.failureThreshold) {
      this.state = 'OPEN'
      this.nextAttempt = Date.now() + this.recoveryTimeout
    }
  }
}

// Usage
const userServiceBreaker = new CircuitBreaker(userService, {
  failureThreshold: 5,
  recoveryTimeout: 60000
})

app.get('/users/:id', async (req, res) => {
  try {
    const user = await userServiceBreaker.call(req)
    res.json(user)
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      res.status(503).json({ error: 'Service temporarily unavailable' })
    }
  }
})
```

## Retry Logic with Backoff

**Exponential Backoff:**
```javascript
async function retryWithBackoff(fn, options = {}) {
  const maxRetries = options.maxRetries || 3
  const baseDelay = options.baseDelay || 1000
  const maxDelay = options.maxDelay || 10000
  const retryableErrors = options.retryableErrors || [502, 503, 504]

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()

    } catch (error) {
      const isLastAttempt = attempt === maxRetries
      const isRetryable = retryableErrors.includes(error.status)

      if (isLastAttempt || !isRetryable) {
        throw error
      }

      // Exponential backoff with jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
        maxDelay
      )

      await sleep(delay)
    }
  }
}

// Gateway usage
app.get('/users/:id', async (req, res) => {
  const user = await retryWithBackoff(
    () => userService.get(req.params.id),
    { maxRetries: 3, baseDelay: 1000 }
  )
  res.json(user)
})
```
