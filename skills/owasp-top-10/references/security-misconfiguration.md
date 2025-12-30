# A05: Security Misconfiguration

**Description:** Missing hardening, unnecessary features, default credentials, verbose errors.

## Common Issues

```javascript
// VULNERABLE: Verbose error messages
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack // Exposes internal structure
  });
});

// SECURE: Generic error messages
app.use((err, req, res, next) => {
  console.error(err); // Log internally only
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id
  });
});

// VULNERABLE: Unnecessary features enabled
app.use(express.static('public', { dotfiles: 'allow' }));
// Exposes .env, .git files

// SECURE: Restrict access
app.use(express.static('public', {
  dotfiles: 'deny',
  index: false // Disable directory listing
}));

// VULNERABLE: Missing security headers
app.get('/', (req, res) => {
  res.send('<h1>Welcome</h1>');
});

// SECURE: Security headers
const helmet = require('helmet');
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## Prevention Checklist

- [ ] Implement automated hardening processes
- [ ] Remove unused features, frameworks, dependencies
- [ ] Review and update configurations regularly
- [ ] Use security headers (CSP, HSTS, X-Frame-Options)
- [ ] Disable default accounts and change default passwords
- [ ] Segment application architecture (containers, cloud)
- [ ] Keep error messages generic, log details internally
