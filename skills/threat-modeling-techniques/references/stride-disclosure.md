# STRIDE: Information Disclosure

**Definition:** Exposing information to unauthorized individuals.

## Threat Examples

### Verbose Error Messages

```javascript
// THREAT: Exposing sensitive data through verbose error messages

// VULNERABLE: Stack traces exposed to users
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    sql: err.sql // Exposes database structure
  });
});

// MITIGATION: Generic errors, detailed internal logs
app.use((err, req, res, next) => {
  // Log internally with full details
  logger.error('Request error', {
    error: err.message,
    stack: err.stack,
    sql: err.sql,
    requestId: req.id,
    userId: req.user?.id
  });

  // Return generic error to client
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id
  });
});
```

## Common Disclosure Vectors

- **Error messages**: Stack traces, database errors, file paths
- **Debug information**: Environment variables, configuration details
- **Source code comments**: Credentials, API keys, internal URLs
- **Directory listings**: Exposed file structure
- **Metadata**: EXIF data, document properties
- **API responses**: Excessive data, internal IDs
- **Network traffic**: Unencrypted communications

## Mitigations

- **Encryption at rest**: AES-256, disk encryption
- **Encryption in transit**: TLS 1.3, certificate pinning
- **Access control enforcement**: RBAC, ABAC, least privilege
- **Data classification**: Mark and handle sensitive data appropriately
- **Secure key management**: KMS, HSM, key rotation
- **Data masking & tokenization**: Protect sensitive fields
- **Generic error messages**: Don't leak internal details to users
- **Security headers**: Prevent MIME sniffing, clickjacking, XSS
- **API response filtering**: Only return necessary fields
- **Secrets scanning**: Detect credentials in code/logs
