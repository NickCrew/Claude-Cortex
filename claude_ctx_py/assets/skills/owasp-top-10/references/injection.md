# A03: Injection

**Description:** Untrusted data sent to interpreters as part of commands or queries.

**Types:** SQL, NoSQL, OS command, LDAP, XPath, template injection

## SQL Injection

```javascript
// VULNERABLE: String concatenation
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
// Attack: username = "admin'--"

// SECURE: Parameterized queries
const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
db.query(query, [username, password]);

// SECURE: ORM with parameterization
const user = await User.findOne({
  where: { username, password }
});
```

## NoSQL Injection

```javascript
// VULNERABLE: Direct object injection
db.collection('users').findOne({
  username: req.body.username,
  password: req.body.password
});
// Attack: { "username": "admin", "password": { "$ne": null } }

// SECURE: Type validation and sanitization
const { username, password } = req.body;
if (typeof username !== 'string' || typeof password !== 'string') {
  return res.status(400).json({ error: 'Invalid input' });
}
db.collection('users').findOne({ username, password });
```

## Command Injection

```javascript
// VULNERABLE: Shell command with user input
const { exec } = require('child_process');
exec(`ping -c 4 ${req.body.host}`, callback);
// Attack: host = "google.com; rm -rf /"

// SECURE: Use safe APIs and validation
const { spawn } = require('child_process');
const host = req.body.host;
if (!/^[a-zA-Z0-9.-]+$/.test(host)) {
  return res.status(400).json({ error: 'Invalid host' });
}
const ping = spawn('ping', ['-c', '4', host]);
```

## Prevention Checklist

- [ ] Use parameterized queries or ORMs exclusively
- [ ] Validate all input against strict allow-lists
- [ ] Escape special characters for the specific interpreter
- [ ] Use LIMIT in SQL queries to minimize data exposure
- [ ] Implement least privilege for database accounts
- [ ] Use static analysis tools (SAST) to detect injection
