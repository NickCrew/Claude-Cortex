# Cryptography Best Practices

## Encryption with AES-256-GCM

```javascript
const crypto = require('crypto');

// SECURE: Symmetric encryption with authenticated encryption
class SecureEncryption {
  constructor() {
    // 256-bit key from environment
    this.key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    if (this.key.length !== 32) {
      throw new Error('Encryption key must be 32 bytes (256 bits)');
    }
    this.algorithm = 'aes-256-gcm';
  }

  encrypt(plaintext) {
    // Generate random IV (96 bits for GCM)
    const iv = crypto.randomBytes(12);

    // Create cipher
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

    // Encrypt data
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);

    // Get authentication tag
    const authTag = cipher.getAuthTag();

    // Return IV + authTag + ciphertext (all needed for decryption)
    return {
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      ciphertext: encrypted.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const iv = Buffer.from(encryptedData.iv, 'hex');
    const authTag = Buffer.from(encryptedData.authTag, 'hex');
    const ciphertext = Buffer.from(encryptedData.ciphertext, 'hex');

    // Create decipher
    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    decipher.setAuthTag(authTag);

    // Decrypt data
    const decrypted = Buffer.concat([
      decipher.update(ciphertext),
      decipher.final()
    ]);

    return decrypted.toString('utf8');
  }
}

// Usage
const encryption = new SecureEncryption();
const encrypted = encryption.encrypt('sensitive data');
const decrypted = encryption.decrypt(encrypted);
```

## Key Management

```javascript
// NEVER hardcode keys in source code
// BAD: const SECRET_KEY = 'hardcoded-secret-123';

// GOOD: Use environment variables
require('dotenv').config();
const SECRET_KEY = process.env.SECRET_KEY;

// BETTER: Use dedicated key management service
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

async function getSecret(secretName) {
  const client = new SecretsManagerClient({ region: 'us-east-1' });
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return response.SecretString;
}

// Key rotation strategy
async function rotateEncryptionKey(oldKey, newKey) {
  const records = await db.sensitiveData.findAll();

  for (const record of records) {
    // Decrypt with old key
    const decrypted = decryptWithKey(record.data, oldKey);

    // Re-encrypt with new key
    const encrypted = encryptWithKey(decrypted, newKey);

    // Update record
    await db.sensitiveData.update(record.id, { data: encrypted });
  }
}
```

## Secure Random Number Generation

```javascript
const crypto = require('crypto');

// VULNERABLE: Predictable randomness
Math.random(); // NEVER use for security

// SECURE: Cryptographically secure randomness
const token = crypto.randomBytes(32).toString('hex'); // 256-bit token
const resetToken = crypto.randomBytes(20).toString('hex'); // Password reset
const sessionId = crypto.randomBytes(16).toString('base64url'); // Session IDs

// SECURE: Random integer in range
function getSecureRandomInt(min, max) {
  const range = max - min;
  const bytesNeeded = Math.ceil(Math.log2(range) / 8);
  const maxValid = Math.floor(256 ** bytesNeeded / range) * range;

  let randomValue;
  do {
    randomValue = crypto.randomBytes(bytesNeeded).readUIntBE(0, bytesNeeded);
  } while (randomValue >= maxValid);

  return min + (randomValue % range);
}
```

## Best Practices

1. **Use AES-256-GCM** - Authenticated encryption prevents tampering
2. **Random IVs** - Generate new IV for each encryption operation
3. **Key management** - Use KMS, never hardcode keys
4. **Secure randomness** - crypto.randomBytes(), never Math.random()
5. **Key rotation** - Implement rotation strategy for long-term keys
6. **Never roll your own** - Use established crypto libraries
7. **Minimum key sizes** - AES-256 (32 bytes), RSA-2048 minimum
8. **Authenticate then encrypt** - Or use authenticated encryption (GCM, Poly1305)
