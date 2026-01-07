# Authentication & Session Management

## Secure Password Handling

```javascript
// SECURE: Password hashing with bcrypt
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12; // Adjusts computational cost

async function registerUser(username, password) {
  // Validate password strength
  if (password.length < 12) {
    throw new Error('Password must be at least 12 characters');
  }

  // Hash password
  const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

  // Store username and hash (NEVER store plaintext)
  await db.users.create({ username, passwordHash });
}

async function authenticateUser(username, password) {
  const user = await db.users.findOne({ username });
  if (!user) {
    // Use constant-time comparison to prevent timing attacks
    await bcrypt.compare(password, '$2b$12$dummy.hash.to.prevent.timing.attack');
    throw new Error('Invalid credentials');
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    throw new Error('Invalid credentials');
  }

  return user;
}
```

## Secure Session Management

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

// Initialize Redis client
const redisClient = createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  password: process.env.REDIS_PASSWORD
});

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET, // Strong random secret
  name: 'sessionId', // Non-default name
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS only
    httpOnly: true, // No JavaScript access
    maxAge: 1800000, // 30 minutes
    sameSite: 'strict', // CSRF protection
    domain: 'example.com',
    path: '/'
  },
  rolling: true, // Reset expiration on activity
  genid: () => {
    // Cryptographically secure session ID
    return require('crypto').randomBytes(32).toString('hex');
  }
}));
```

## JWT Best Practices

```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// SECURE: JWT implementation
const JWT_SECRET = process.env.JWT_SECRET; // Strong random secret
const JWT_EXPIRY = '15m'; // Short expiration
const REFRESH_TOKEN_EXPIRY = '7d';

function generateTokens(userId) {
  // Access token (short-lived)
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRY, algorithm: 'HS256' }
  );

  // Refresh token (long-lived, stored securely)
  const refreshToken = jwt.sign(
    { userId, type: 'refresh', jti: crypto.randomBytes(16).toString('hex') },
    JWT_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY, algorithm: 'HS256' }
  );

  return { accessToken, refreshToken };
}

function verifyAccessToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid token' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });

    if (decoded.type !== 'access') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    req.user = { userId: decoded.userId };
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

## Multi-Factor Authentication (MFA)

```javascript
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

// Enable TOTP-based MFA
async function enableMFA(userId) {
  const secret = speakeasy.generateSecret({
    name: `MyApp (${userId})`,
    length: 32
  });

  // Store secret.base32 encrypted in database
  await db.users.update(userId, {
    mfaSecret: encrypt(secret.base32),
    mfaEnabled: false // Activated after verification
  });

  // Generate QR code for user to scan
  const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

  return { secret: secret.base32, qrCode: qrCodeUrl };
}

function verifyMFAToken(secret, token) {
  return speakeasy.totp.verify({
    secret,
    encoding: 'base32',
    token,
    window: 2 // Allow 2 time steps for clock drift
  });
}
```

## Best Practices

1. **Hash passwords** - Use bcrypt/Argon2 with salt rounds ≥12
2. **Constant-time comparisons** - Prevent timing attacks
3. **Secure session cookies** - HttpOnly, Secure, SameSite
4. **Short-lived tokens** - JWT access tokens expire quickly
5. **MFA for sensitive operations** - Add second authentication factor
6. **Rate limiting** - Prevent brute force attacks
7. **Session regeneration** - Generate new session ID on login
