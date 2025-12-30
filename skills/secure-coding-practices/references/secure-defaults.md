# Secure Defaults & Configuration

## Security Headers

```javascript
const helmet = require('helmet');

// Apply secure defaults
app.use(helmet({
  // Prevent clickjacking
  frameguard: { action: 'deny' },

  // Enforce HTTPS
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true
  },

  // Prevent MIME sniffing
  noSniff: true,

  // XSS protection
  xssFilter: true,

  // Referrer policy
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },

  // Permissions policy
  permissionsPolicy: {
    features: {
      geolocation: ["'self'"],
      camera: ["'none'"],
      microphone: ["'none'"]
    }
  }
}));

// CORS configuration
const cors = require('cors');
app.use(cors({
  origin: ['https://trusted-domain.com'],
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400 // 24 hours
}));
```

## Principle of Least Privilege

```javascript
// Database: Create limited-privilege users
// NEVER use root/admin for application connections

// PostgreSQL example:
/*
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT ON products TO app_user;
-- Do NOT grant DELETE, DROP, or admin privileges
*/

// Application: Role-based access control
const roles = {
  USER: ['read:profile', 'update:profile'],
  MODERATOR: ['read:profile', 'update:profile', 'delete:comments'],
  ADMIN: ['read:profile', 'update:profile', 'delete:comments', 'manage:users']
};

function authorize(requiredPermission) {
  return (req, res, next) => {
    const userRole = req.user.role;
    const permissions = roles[userRole] || [];

    if (!permissions.includes(requiredPermission)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

app.delete('/api/users/:id', authenticate, authorize('manage:users'), (req, res) => {
  deleteUser(req.params.id);
});
```

## Secure Configuration Management

```javascript
// Environment-based configuration
const config = {
  development: {
    database: {
      host: 'localhost',
      ssl: false,
      debug: true
    },
    logging: 'debug'
  },
  production: {
    database: {
      host: process.env.DB_HOST,
      ssl: {
        rejectUnauthorized: true,
        ca: fs.readFileSync('/path/to/ca-cert.pem')
      },
      debug: false
    },
    logging: 'error'
  }
};

const env = process.env.NODE_ENV || 'development';
const activeConfig = config[env];

// Fail securely
if (env === 'production' && !activeConfig.database.ssl) {
  throw new Error('SSL required for production database');
}
```

## Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

// General rate limiting
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests, please try again later'
});

// Strict rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 login attempts per 15 minutes
  skipSuccessfulRequests: true
});

app.use('/api/', generalLimiter);
app.use('/api/auth/', authLimiter);
```

## Best Practices

1. **Secure by default** - All features locked down, explicitly enable what's needed
2. **Deny by default** - Reject unless explicitly allowed
3. **Fail securely** - Errors should default to secure state
4. **Least privilege** - Minimal permissions necessary for function
5. **Defense in depth** - Multiple layers of security controls
6. **Security headers** - Use helmet.js for comprehensive protection
7. **Rate limiting** - Prevent abuse and DoS attacks
8. **Environment separation** - Different configs for dev/staging/production
