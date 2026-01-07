# A04: Insecure Design

**Description:** Missing or ineffective security controls in design phase.

## Threat Modeling Examples

```javascript
// INSECURE DESIGN: No rate limiting on sensitive endpoints
app.post('/api/login', async (req, res) => {
  const user = await authenticate(req.body);
  // Vulnerable to credential stuffing
});

// SECURE DESIGN: Rate limiting + CAPTCHA
const rateLimit = require('express-rate-limit');
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true
});

app.post('/api/login', loginLimiter, async (req, res) => {
  if (req.session.failedAttempts >= 3) {
    const captchaValid = await verifyCaptcha(req.body.captcha);
    if (!captchaValid) {
      return res.status(400).json({ error: 'Invalid CAPTCHA' });
    }
  }
  const user = await authenticate(req.body);
});

// INSECURE DESIGN: No transaction limits
app.post('/api/transfer', authenticate, async (req, res) => {
  await transferFunds(req.user.id, req.body.to, req.body.amount);
});

// SECURE DESIGN: Transaction limits + verification
app.post('/api/transfer', authenticate, async (req, res) => {
  const { to, amount } = req.body;

  // Business logic validation
  if (amount > 10000) {
    const verified = await require2FA(req.user);
    if (!verified) {
      return res.status(403).json({ error: '2FA required for large transfers' });
    }
  }

  // Daily limit check
  const dailyTotal = await getDailyTransferTotal(req.user.id);
  if (dailyTotal + amount > 50000) {
    return res.status(403).json({ error: 'Daily limit exceeded' });
  }

  await transferFunds(req.user.id, to, amount);
});
```

## Design Principles

- Establish secure development lifecycle (SDLC)
- Use threat modeling (STRIDE, PASTA, OCTAVE)
- Write security user stories and abuse cases
- Implement defense in depth (layered security)
- Separate tenants and layers by design
- Limit resource consumption per user/tenant
