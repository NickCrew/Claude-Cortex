# A09: Security Logging and Monitoring Failures

**Description:** Insufficient logging and monitoring allowing breaches to go undetected.

## Effective Logging

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'security.log' })
  ]
});

// Log security events
app.post('/api/login', async (req, res) => {
  try {
    const user = await authenticate(req.body);
    logger.info('Login success', {
      userId: user.id,
      ip: req.ip,
      timestamp: new Date()
    });
  } catch (err) {
    logger.warn('Login failed', {
      username: req.body.username,
      ip: req.ip,
      timestamp: new Date()
    });
  }
});
```

## Critical Events to Log

- Login/logout (success and failures)
- Access control failures (authorization denials)
- Input validation failures
- Authentication token anomalies
- Server-side exceptions and errors
- Administrative actions
- Privilege escalation attempts
- Data access and modifications
- Sensitive configuration changes

## Prevention

- Ensure logs are tamper-proof (append-only)
- Implement centralized log management (SIEM)
- Establish effective monitoring and alerting
- Define incident response and recovery plan
- Use correlation IDs to track requests
- Set appropriate log retention policies
- Protect logs from unauthorized access
- Ensure log formats support automated analysis
- Alert on suspicious patterns in real-time
- Test logging and alerting regularly
