# Input Validation & Sanitization

**Principle:** Never trust user input. Validate all data from untrusted sources before processing.

## Allowlist Validation

```javascript
// VULNERABLE: Blocklist approach (incomplete, bypassable)
function validateUsername(username) {
  const blocked = ['admin', 'root', 'system'];
  return !blocked.includes(username);
}

// SECURE: Allowlist approach (explicit, comprehensive)
function validateUsername(username) {
  // Only allow alphanumeric characters, underscores, and hyphens
  const pattern = /^[a-zA-Z0-9_-]{3,20}$/;
  return pattern.test(username);
}

// SECURE: Multi-layered validation
function validateEmail(email) {
  // 1. Type check
  if (typeof email !== 'string') return false;

  // 2. Length validation
  if (email.length > 254) return false;

  // 3. Format validation
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) return false;

  // 4. Domain validation (optional)
  const allowedDomains = ['example.com', 'trusted.org'];
  const domain = email.split('@')[1];
  if (!allowedDomains.includes(domain)) return false;

  return true;
}
```

## Server-Side Validation

```javascript
// NEVER trust client-side validation alone
const express = require('express');
const { body, validationResult } = require('express-validator');

app.post('/api/register',
  // Define validation rules
  [
    body('email')
      .isEmail()
      .normalizeEmail()
      .withMessage('Invalid email format'),
    body('password')
      .isLength({ min: 12 })
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/)
      .withMessage('Password must be 12+ chars with upper, lower, number, special char'),
    body('age')
      .isInt({ min: 18, max: 120 })
      .withMessage('Age must be between 18 and 120'),
  ],
  (req, res) => {
    // Check validation results
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Proceed with validated data
    createUser(req.body);
  }
);
```

## Type Coercion Defense

```javascript
// VULNERABLE: Loose comparison
if (req.body.isAdmin == true) {
  grantAdminAccess();
}
// Attack: isAdmin = "true" or isAdmin = 1

// SECURE: Strict type checking
if (req.body.isAdmin === true && typeof req.body.isAdmin === 'boolean') {
  grantAdminAccess();
}

// SECURE: Schema validation with libraries
const Joi = require('joi');

const userSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(18).max(120).required(),
  isAdmin: Joi.boolean().required()
});

const { error, value } = userSchema.validate(req.body);
if (error) {
  return res.status(400).json({ error: error.details[0].message });
}
```

## Best Practices

1. **Always validate server-side** - Never trust client-side validation alone
2. **Use allowlists** - Define what's acceptable, not what's forbidden
3. **Layer validations** - Type → Length → Format → Business rules
4. **Use schema libraries** - Joi, Yup, Zod for comprehensive validation
5. **Sanitize after validation** - Clean data before processing
6. **Fail securely** - Reject invalid input, don't try to "fix" it
