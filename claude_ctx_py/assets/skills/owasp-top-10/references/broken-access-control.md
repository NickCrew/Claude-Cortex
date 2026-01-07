# A01: Broken Access Control

**Description:** Users can act outside their intended permissions, accessing unauthorized data or functions.

## Common Patterns

```javascript
// VULNERABLE: Direct object reference without authorization
app.get('/api/users/:id/profile', (req, res) => {
  const profile = db.getProfile(req.params.id);
  res.json(profile); // No check if user can access this profile
});

// VULNERABLE: Path traversal
app.get('/files/:filename', (req, res) => {
  res.sendFile(`./uploads/${req.params.filename}`);
  // Attack: GET /files/../../etc/passwd
});

// VULNERABLE: Missing function-level access control
app.post('/api/admin/users', (req, res) => {
  // No admin role check
  createUser(req.body);
});
```

## Secure Implementation

```javascript
// SECURE: Verify authorization for each request
app.get('/api/users/:id/profile', authenticate, (req, res) => {
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const profile = db.getProfile(req.params.id);
  res.json(profile);
});

// SECURE: Sanitize file paths
const path = require('path');
app.get('/files/:filename', authenticate, (req, res) => {
  const filename = path.basename(req.params.filename);
  const filepath = path.join(__dirname, 'uploads', filename);

  if (!filepath.startsWith(path.join(__dirname, 'uploads'))) {
    return res.status(400).json({ error: 'Invalid path' });
  }
  res.sendFile(filepath);
});

// SECURE: Function-level access control
app.post('/api/admin/users', authenticate, requireRole('admin'), (req, res) => {
  createUser(req.body);
});
```

## Prevention Checklist

- [ ] Deny by default, explicit allow for authorized access
- [ ] Implement attribute-based or role-based access control (ABAC/RBAC)
- [ ] Disable directory listing on web servers
- [ ] Log access control failures and alert on repeated violations
- [ ] Invalidate JWT tokens on logout
- [ ] Rate-limit API endpoints to minimize automated attacks
