# STRIDE: Denial of Service

**Definition:** Making systems unavailable to legitimate users.

## Threat Examples

### Resource Exhaustion

```javascript
// THREAT: Resource exhaustion through unbounded operations

// VULNERABLE: No rate limiting or resource constraints
app.post('/api/search', async (req, res) => {
  const results = await db.query(`SELECT * FROM products WHERE name LIKE '%${req.body.query}%'`);
  res.json(results); // Returns unlimited rows
});

// MITIGATION: Rate limiting + pagination + timeouts
const rateLimit = require('express-rate-limit');

const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 20 // 20 requests per minute
});

app.post('/api/search', searchLimiter, async (req, res) => {
  const query = req.body.query;
  const page = parseInt(req.body.page) || 1;
  const limit = Math.min(parseInt(req.body.limit) || 10, 100); // Max 100 items
  const offset = (page - 1) * limit;

  // Use parameterized query with LIMIT
  const results = await db.query(
    'SELECT * FROM products WHERE name LIKE ? LIMIT ? OFFSET ?',
    [`%${query}%`, limit, offset],
    { timeout: 5000 } // 5 second query timeout
  );

  res.json({
    results,
    page,
    limit,
    hasMore: results.length === limit
  });
});
```

## DoS Attack Vectors

- **Application layer**: Expensive operations, algorithmic complexity
- **Network layer**: SYN floods, UDP floods, amplification attacks
- **Resource exhaustion**: Memory leaks, CPU spinning, disk filling
- **Logic bombs**: Triggering expensive operations repeatedly
- **Distributed attacks (DDoS)**: Coordinated botnet attacks

## Mitigations

- **Rate limiting & throttling**: Per-user, per-IP, per-endpoint limits
- **Resource quotas**: Memory limits, CPU time, disk space
- **Timeouts**: Request timeouts, query timeouts, connection timeouts
- **Input validation**: Size limits, complexity limits, format validation
- **Load balancing**: Distribute traffic across multiple servers
- **Auto-scaling**: Horizontal scaling based on load
- **CDN & caching**: Reduce load on origin servers
- **Anti-automation**: CAPTCHA, proof-of-work challenges
- **DDoS protection**: Cloudflare, AWS Shield, Akamai
- **Circuit breakers**: Fail fast when dependencies are down
- **Backpressure**: Push back on clients when overwhelmed
