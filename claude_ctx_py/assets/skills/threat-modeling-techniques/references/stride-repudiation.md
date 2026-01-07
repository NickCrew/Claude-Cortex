# STRIDE: Repudiation

**Definition:** Denying actions or transactions without proof otherwise.

## Threat Examples

### Missing Audit Trail

```javascript
// THREAT: User denies performing sensitive action without audit trail

// VULNERABLE: No audit logging
app.post('/api/transfer', authenticate, async (req, res) => {
  await transferFunds(req.user.id, req.body.to, req.body.amount);
  res.json({ success: true });
});

// MITIGATION: Comprehensive audit logging
const winston = require('winston');
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'audit.log' })
  ]
});

app.post('/api/transfer', authenticate, async (req, res) => {
  const auditEvent = {
    action: 'FUND_TRANSFER',
    userId: req.user.id,
    from: req.user.accountId,
    to: req.body.to,
    amount: req.body.amount,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date().toISOString(),
    sessionId: req.session.id
  };

  logger.info('Fund transfer initiated', auditEvent);

  try {
    const result = await transferFunds(req.user.id, req.body.to, req.body.amount);
    logger.info('Fund transfer completed', { ...auditEvent, transactionId: result.id });
    res.json({ success: true, transactionId: result.id });
  } catch (err) {
    logger.error('Fund transfer failed', { ...auditEvent, error: err.message });
    res.status(500).json({ error: 'Transfer failed' });
  }
});
```

## Mitigations

- **Comprehensive audit logging**: Who, what, when, where, why
- **Digital signatures**: Cryptographic non-repudiation
- **Tamper-proof log storage**: Append-only, immutable logs
- **Secure time-stamping**: Trusted time sources
- **Multi-party approval**: Require multiple signatures for critical actions
- **Legal agreements**: Terms of service, audit clauses
- **Blockchain/distributed ledger**: Immutable transaction records
