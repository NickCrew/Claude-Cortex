# Documentation Patterns Reference

API doc structure, glossary patterns, cross-referencing techniques, versioned documentation,
parameter tables, and configuration guide patterns.

---

## API Documentation Structure

### REST API Entry Template

```markdown
## POST /api/users

Create a new user account.

**Authentication**: Required (Bearer token)
**Rate Limit**: 10 requests/minute per token
**Since**: v2.0.0

### Request

**Headers**:

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `Content-Type` | Yes | Must be `application/json` |
| `Idempotency-Key` | No | Prevents duplicate creation |

**Body**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | `string` | Yes | 1-100 chars | Display name |
| `email` | `string` | Yes | Valid email format | Unique email address |
| `role` | `string` | No | One of: `user`, `admin` | Default: `user` |

**Example**:
\`\`\`json
{
  "name": "Jane Developer",
  "email": "jane@example.com",
  "role": "admin"
}
\`\`\`

### Response

**Success (201 Created)**:
\`\`\`json
{
  "id": "usr_abc123",
  "name": "Jane Developer",
  "email": "jane@example.com",
  "role": "admin",
  "created_at": "2026-01-15T10:30:00Z"
}
\`\`\`

**Errors**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | `invalid_email` | Email format is invalid |
| 409 | `email_exists` | Email already registered |
| 422 | `validation_error` | One or more fields failed validation |
| 429 | `rate_limited` | Rate limit exceeded |

**Error response format**:
\`\`\`json
{
  "error": {
    "code": "email_exists",
    "message": "A user with this email already exists",
    "field": "email"
  }
}
\`\`\`
```

### GraphQL API Entry Template

```markdown
## Query: users

Fetch a paginated list of users with optional filtering.

**Authentication**: Required
**Since**: v2.1.0

### Schema

\`\`\`graphql
type Query {
  users(
    filter: UserFilter
    pagination: PaginationInput
    sort: UserSort
  ): UserConnection!
}

input UserFilter {
  role: UserRole
  createdAfter: DateTime
  search: String
}

input PaginationInput {
  first: Int = 20
  after: String
}

enum UserSort {
  CREATED_AT_ASC
  CREATED_AT_DESC
  NAME_ASC
}
\`\`\`

### Example Query

\`\`\`graphql
query {
  users(filter: { role: ADMIN }, pagination: { first: 10 }) {
    edges {
      node {
        id
        name
        email
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
\`\`\`
```

### CLI Command Entry Template

```markdown
## cortex deploy

Deploy the application to the specified environment.

**Since**: v1.0.0

### Usage

\`\`\`bash
cortex deploy [environment] [flags]
\`\`\`

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `environment` | No | `staging` | Target environment |

### Flags

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--config` | `-c` | `string` | `./deploy.yaml` | Config file path |
| `--dry-run` | | `bool` | `false` | Show what would be deployed |
| `--timeout` | `-t` | `duration` | `5m` | Deploy timeout |
| `--force` | `-f` | `bool` | `false` | Skip confirmation prompt |
| `--verbose` | `-v` | `bool` | `false` | Verbose output |

### Examples

\`\`\`bash
# Deploy to staging (default)
cortex deploy

# Deploy to production with confirmation
cortex deploy production

# Dry run to see what would change
cortex deploy production --dry-run

# Deploy with custom config
cortex deploy staging -c ./custom-deploy.yaml
\`\`\`

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Timeout |
| 4 | Authentication failure |
```

---

## Parameter Tables

### Standard Parameter Table

Always use this format for consistency:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | `string` | Yes | — | Human-readable name |
| `timeout` | `number` | No | `30000` | Timeout in milliseconds |
| `retries` | `number` | No | `3` | Number of retry attempts (0-10) |
| `mode` | `string` | No | `"auto"` | One of: `"auto"`, `"manual"`, `"disabled"` |

### Nested Parameter Tables

For complex objects, use indentation or separate tables:

```markdown
### Options

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `connection` | `object` | Yes | — | Database connection settings |
| `connection.host` | `string` | Yes | — | Database hostname |
| `connection.port` | `number` | No | `5432` | Database port |
| `connection.ssl` | `boolean` | No | `true` | Enable TLS |
| `pool` | `object` | No | — | Connection pool settings |
| `pool.min` | `number` | No | `2` | Minimum pool size |
| `pool.max` | `number` | No | `10` | Maximum pool size |
```

### Enum Tables

When a parameter accepts specific values, document each:

```markdown
### Status Values

| Value | Description | Transitions to |
|-------|-------------|---------------|
| `draft` | Initial state, editable | `review` |
| `review` | Under review, read-only | `approved`, `draft` |
| `approved` | Approved, awaiting publish | `published` |
| `published` | Live and visible to users | `archived` |
| `archived` | No longer visible | `draft` |
```

---

## Configuration Guide Patterns

### Configuration File Reference

```markdown
## Configuration Reference

Configuration is loaded from `config.yaml` in the project root. All values can
be overridden with environment variables using the `APP_` prefix.

### Server

\`\`\`yaml
server:
  port: 3000          # APP_SERVER_PORT — Port to listen on (1024-65535)
  host: "0.0.0.0"     # APP_SERVER_HOST — Bind address
  timeout: 30000      # APP_SERVER_TIMEOUT — Request timeout in ms
  cors:
    enabled: true     # APP_SERVER_CORS_ENABLED — Enable CORS
    origins:          # APP_SERVER_CORS_ORIGINS — Comma-separated origins
      - "https://app.example.com"
\`\`\`

| Key | Type | Default | Env Var | Description |
|-----|------|---------|---------|-------------|
| `server.port` | `integer` | `3000` | `APP_SERVER_PORT` | TCP port (1024-65535) |
| `server.host` | `string` | `"0.0.0.0"` | `APP_SERVER_HOST` | Bind address |
| `server.timeout` | `integer` | `30000` | `APP_SERVER_TIMEOUT` | Request timeout (ms) |
| `server.cors.enabled` | `boolean` | `true` | `APP_SERVER_CORS_ENABLED` | Enable CORS headers |
| `server.cors.origins` | `string[]` | `["*"]` | `APP_SERVER_CORS_ORIGINS` | Allowed origins |
```

### Environment-Specific Overrides

```markdown
### Environment Defaults

Values that change by environment:

| Key | Development | Staging | Production |
|-----|------------|---------|------------|
| `server.port` | `3000` | `8080` | `8080` |
| `database.pool.max` | `5` | `20` | `50` |
| `logging.level` | `debug` | `info` | `warn` |
| `cache.ttl` | `0` (disabled) | `300` | `3600` |
```

---

## Glossary Patterns

### Glossary Entry Format

```markdown
## Glossary

**Bearer Token**: An access token included in the `Authorization` header as
`Bearer <token>`. Obtained from the [authentication endpoint](#post-apiauth).

**CDE (Cardholder Data Environment)**: The systems, networks, and processes that
store, process, or transmit cardholder data. See [PCI DSS scope](#pci-dss-scope).

**Idempotency Key**: A unique string sent with mutating requests to prevent
duplicate operations. The server guarantees that requests with the same key
produce the same result. See [idempotency guide](#idempotency).
```

### Glossary Rules

- Sort alphabetically
- Include the abbreviation expansion if applicable
- Link to the relevant documentation section
- Keep definitions to 1-3 sentences
- Use consistent formatting (bold term, colon, definition)

---

## Cross-Referencing Techniques

### In-Document Links

```markdown
See the [authentication section](#authentication) for details on token management.
```

### Cross-Document Links

```markdown
For deployment configuration, see the [Operations Guide](./operations.md#deployment).
```

### "See Also" Blocks

Place at the end of each entry:

```markdown
**See Also**:
- [Related Method](#related-method) — does something similar for a different use case
- [Configuration Guide](#configuration) — configure the defaults for this method
- [Error Codes](#error-codes) — full list of errors this method can return
```

### Back-References

When documenting errors, link back to the operations that produce them:

```markdown
### Error: `rate_limited` (429)

**Produced by**: [POST /api/users](#post-apiusers), [POST /api/orders](#post-apiorders)

**Description**: Request rate limit exceeded for your API token.

**Resolution**: Wait for the duration specified in the `Retry-After` header.
```

---

## Versioned Documentation

### Version Badges

Mark entries with the version they were introduced or changed:

```markdown
### newMethod() <Badge text="v2.1.0" />

Description...

### legacyMethod() <Badge text="Deprecated in v3.0" type="warning" />

**Deprecated**: Use [newMethod](#newmethod) instead. Will be removed in v4.0.
```

### In Markdown (Without Components)

```markdown
### newMethod()

> **Added in v2.1.0**

### legacyMethod()

> **Deprecated in v3.0** — Use [newMethod](#newmethod) instead. Removal planned for v4.0.
```

### Changelog Section

Place at the bottom of reference docs:

```markdown
## Changelog

### v3.0.0 (2026-02-01)
- **Breaking**: Removed `legacyMethod()` — use `newMethod()` instead
- **Breaking**: Changed `timeout` default from 60s to 30s
- Added `batchProcess()` method

### v2.1.0 (2025-11-15)
- Added `newMethod()` for improved performance
- Deprecated `legacyMethod()` (removal in v4.0)
- Added `retries` parameter to `connect()`

### v2.0.0 (2025-08-01)
- Initial stable release
```

---

## Searchable Indexing

### Keyword Embedding

Include search terms that users might use but that are not in the heading:

```markdown
### connect()
<!-- keywords: open connection, establish session, initialize client, setup -->

Opens a connection to the server.
```

### Alias Documentation

When the same concept has multiple names:

```markdown
### Rate Limiting (Throttling)

Also known as: request throttling, API rate control, traffic shaping.
```

### Index Table

For large reference docs, provide an alphabetical index:

```markdown
## Index

| Term | Section |
|------|---------|
| Authentication | [Authentication](#authentication) |
| Authorization header | [Headers](#headers) |
| Bearer token | [Authentication](#authentication), [Glossary](#glossary) |
| CORS | [Configuration](#cors-configuration) |
| Rate limiting | [Rate Limiting](#rate-limiting) |
| Retry-After header | [Rate Limiting](#rate-limiting), [Headers](#headers) |
```
