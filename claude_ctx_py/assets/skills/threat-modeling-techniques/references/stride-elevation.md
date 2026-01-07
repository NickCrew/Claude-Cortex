# STRIDE: Elevation of Privilege

**Definition:** Gaining capabilities without proper authorization.

## Threat Examples

### Parameter Manipulation

```javascript
// THREAT: Privilege escalation through parameter manipulation

// VULNERABLE: Client-controlled role assignment
app.post('/api/users', authenticate, async (req, res) => {
  const user = await db.createUser({
    username: req.body.username,
    password: req.body.password,
    role: req.body.role // Attacker sets role: 'admin'
  });
  res.json(user);
});

// MITIGATION: Server-side role enforcement
app.post('/api/users', authenticate, requireRole('admin'), async (req, res) => {
  // Only admins can create users
  // Default role assigned by system, not client
  const user = await db.createUser({
    username: req.body.username,
    password: req.body.password,
    role: 'user', // Always default to least privilege
    createdBy: req.user.id
  });

  logger.info('User created', {
    newUserId: user.id,
    createdBy: req.user.id,
    timestamp: new Date()
  });

  res.json(user);
});

// Separate endpoint for role changes with strict controls
app.patch('/api/users/:id/role', authenticate, requireRole('admin'), async (req, res) => {
  const targetUser = await db.getUser(req.params.id);

  // Prevent self-elevation
  if (targetUser.id === req.user.id) {
    return res.status(403).json({ error: 'Cannot modify own role' });
  }

  // Validate role value
  const validRoles = ['user', 'moderator', 'admin'];
  if (!validRoles.includes(req.body.role)) {
    return res.status(400).json({ error: 'Invalid role' });
  }

  await db.updateUser(req.params.id, { role: req.body.role });

  logger.warn('Role changed', {
    targetUserId: targetUser.id,
    oldRole: targetUser.role,
    newRole: req.body.role,
    changedBy: req.user.id,
    timestamp: new Date()
  });

  res.json({ success: true });
});
```

## Privilege Escalation Vectors

- **Horizontal escalation**: Access another user's resources
- **Vertical escalation**: Gain higher privileges (user → admin)
- **Parameter manipulation**: Modify request parameters (user ID, role)
- **Path traversal**: Access restricted directories/files
- **SQL injection**: Bypass authorization checks
- **Insecure direct object references (IDOR)**: Access objects without authorization

## Mitigations

- **Principle of least privilege**: Grant minimum required permissions
- **Role-based access control (RBAC)**: Define and enforce roles
- **Input validation**: Validate all privilege-related parameters
- **Separation of duties**: Require multiple approvals for sensitive actions
- **Privilege use logging**: Audit all privilege changes and usage
- **Secure defaults**: Deny by default, explicit allow
- **Regular privilege audits**: Review and revoke unused permissions
- **Attribute-based access control (ABAC)**: Fine-grained access control
- **Just-in-time (JIT) access**: Temporary elevated privileges
