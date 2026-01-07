# Output Encoding & Context-Aware Escaping

**Principle:** Encode all output based on the context where it will be used.

## HTML Context Escaping

```javascript
// VULNERABLE: Direct output without encoding
app.get('/welcome', (req, res) => {
  const name = req.query.name;
  res.send(`<h1>Welcome ${name}!</h1>`);
  // XSS: /welcome?name=<script>alert('XSS')</script>
});

// SECURE: HTML entity encoding
const escapeHtml = (str) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  return str.replace(/[&<>"'/]/g, (char) => map[char]);
};

app.get('/welcome', (req, res) => {
  const name = escapeHtml(req.query.name);
  res.send(`<h1>Welcome ${name}!</h1>`);
});

// BETTER: Use templating engines with auto-escaping
const handlebars = require('handlebars');
const template = handlebars.compile('<h1>Welcome {{name}}!</h1>');
app.get('/welcome', (req, res) => {
  res.send(template({ name: req.query.name }));
});
```

## JavaScript Context Escaping

```javascript
// VULNERABLE: Injecting into JavaScript
res.send(`
  <script>
    var username = "${req.query.username}";
  </script>
`);
// Attack: username="; alert('XSS'); //

// SECURE: JSON encoding for JavaScript context
res.send(`
  <script>
    var username = ${JSON.stringify(req.query.username)};
  </script>
`);
```

## URL Context Encoding

```javascript
// VULNERABLE: Unencoded URL parameter
const redirectUrl = `/profile?user=${req.query.user}`;
// Attack: user=admin&admin=true

// SECURE: Proper URL encoding
const redirectUrl = `/profile?user=${encodeURIComponent(req.query.user)}`;
```

## Content Security Policy (CSP)

```javascript
// Implement CSP headers to prevent XSS
const helmet = require('helmet');

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-{random}'"], // Use nonces for inline scripts
    styleSrc: ["'self'", "https://trusted-cdn.com"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    frameSrc: ["'none'"],
    upgradeInsecureRequests: []
  }
}));
```

## Best Practices

1. **Context-aware encoding** - HTML, JavaScript, URL, CSS, SQL each need different escaping
2. **Use templating engines** - Modern frameworks auto-escape by default
3. **Implement CSP** - Defense-in-depth against XSS
4. **Never trust innerHTML** - Use textContent or sanitization libraries
5. **Validate and encode** - Both are necessary, neither alone is sufficient
