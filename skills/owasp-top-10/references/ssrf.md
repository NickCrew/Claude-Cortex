# A10: Server-Side Request Forgery (SSRF)

**Description:** Application fetches remote resources without validating user-supplied URLs.

## Vulnerability

```javascript
// VULNERABLE: Fetching user-supplied URLs
app.get('/fetch', async (req, res) => {
  const data = await fetch(req.query.url);
  res.send(await data.text());
  // Attack: /fetch?url=http://localhost:6379/
  // Access internal services (Redis, databases)
});

// SECURE: Validate and restrict URLs
const { URL } = require('url');
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];

app.get('/fetch', async (req, res) => {
  try {
    const url = new URL(req.query.url);

    // Block internal IPs
    const hostname = url.hostname;
    if (hostname === 'localhost' ||
        hostname.startsWith('127.') ||
        hostname.startsWith('192.168.') ||
        hostname.startsWith('10.') ||
        hostname.startsWith('169.254.')) {
      return res.status(400).json({ error: 'Invalid URL' });
    }

    // Allow-list hostnames
    if (!ALLOWED_HOSTS.includes(hostname)) {
      return res.status(400).json({ error: 'Host not allowed' });
    }

    const data = await fetch(url.href);
    res.send(await data.text());
  } catch (err) {
    res.status(400).json({ error: 'Invalid URL' });
  }
});
```

## Prevention

- Sanitize and validate all client-supplied input data
- Enforce URL schema, port, destination with allow-list
- Disable HTTP redirections
- Use network segmentation to separate critical services
- Implement deny-by-default firewall policies
- Use DNS resolution validation
- Implement response validation (content-type, size)
- Use separate network for outbound requests
- Monitor and log all outbound requests
- Implement timeout and size limits on responses
