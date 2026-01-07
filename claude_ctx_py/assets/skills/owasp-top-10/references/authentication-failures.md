# A07: Identification and Authentication Failures

**Description:** Weaknesses in authentication mechanisms allowing attackers to compromise accounts.

## Common Weaknesses

```javascript
// VULNERABLE: Weak session management
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  req.session.userId = user.id; // Predictable session ID
  req.session.cookie.secure = false; // Transmitted over HTTP
});

// SECURE: Strong session management
const session = require('express-session');
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS only
    httpOnly: true, // No JavaScript access
    maxAge: 3600000, // 1 hour
    sameSite: 'strict'
  },
  name: 'sessionId', // Custom name, not default 'connect.sid'
}));
```

## Best Practices

- Implement multi-factor authentication (MFA)
- Use strong password policies (length, complexity, breach detection)
- Harden registration and credential recovery flows
- Limit or delay failed login attempts
- Use cryptographically random session identifiers
- Invalidate sessions on logout and timeout
- Implement account lockout after repeated failures
- Use secure password reset mechanisms
- Avoid exposing session IDs in URLs
- Rotate session IDs after login
- Check passwords against breached password databases (Have I Been Pwned)
