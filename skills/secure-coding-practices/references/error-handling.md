# Error Handling & Logging Security

## Secure Error Handling

```javascript
// VULNERABLE: Exposing stack traces to users
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack, // Leaks internal paths, dependencies
    query: req.query // Leaks user input
  });
});

// SECURE: Generic error messages with internal logging
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

app.use((err, req, res, next) => {
  // Log full error details internally
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userId: req.user?.id,
    requestId: req.id,
    timestamp: new Date().toISOString()
  });

  // Return generic message to user
  res.status(500).json({
    error: 'An internal error occurred',
    requestId: req.id // For support inquiries
  });
});
```

## Safe Logging Practices

```javascript
// NEVER log sensitive data
logger.info('User login', {
  username: user.username,
  password: user.password, // NEVER!
  creditCard: user.card // NEVER!
});

// SECURE: Sanitize before logging
function sanitizeForLogging(obj) {
  const sensitiveFields = ['password', 'creditCard', 'ssn', 'token', 'secret'];
  const sanitized = { ...obj };

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
}

logger.info('User login', sanitizeForLogging({
  username: user.username,
  password: user.password,
  ip: req.ip
}));
// Logs: { username: 'john', password: '[REDACTED]', ip: '192.168.1.1' }

// Log security events
logger.warn('Failed login attempt', {
  username: req.body.username,
  ip: req.ip,
  timestamp: new Date().toISOString()
});

logger.info('Authorization failure', {
  userId: req.user.id,
  resource: req.path,
  action: req.method,
  timestamp: new Date().toISOString()
});
```

## Structured Logging

```javascript
// Use correlation IDs to track requests
const { v4: uuidv4 } = require('uuid');

app.use((req, res, next) => {
  req.id = uuidv4();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// Log with consistent structure
logger.info('Request received', {
  requestId: req.id,
  method: req.method,
  path: req.path,
  userId: req.user?.id,
  ip: req.ip,
  userAgent: req.headers['user-agent']
});
```

## Security Event Logging

Events to always log:
- Authentication attempts (success and failure)
- Authorization failures
- Input validation failures
- Security configuration changes
- Administrative actions
- Sensitive data access
- Rate limit violations
- Suspicious patterns

## Best Practices

1. **Generic error messages** - Never expose stack traces or internal details to users
2. **Comprehensive internal logging** - Log everything internally with full context
3. **Sanitize sensitive data** - Redact passwords, tokens, PII before logging
4. **Correlation IDs** - Track requests across services with unique IDs
5. **Security event monitoring** - Alert on suspicious patterns
6. **Structured logging** - Use JSON format for machine parsing
7. **Log rotation** - Prevent disk space exhaustion
8. **Secure log storage** - Protect logs from tampering, encrypt if sensitive
