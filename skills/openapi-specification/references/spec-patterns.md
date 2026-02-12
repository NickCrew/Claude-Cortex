# OpenAPI Specification Patterns Reference

Patterns, conventions, and techniques for designing robust OpenAPI 3.x specifications.

## OpenAPI 3.x Structure

### Top-Level Organization

```yaml
openapi: 3.1.0          # Specification version

info:                    # API metadata
  title: My API
  version: 1.0.0
  description: ...
  contact: ...
  license: ...

servers:                 # Base URLs
  - url: https://api.example.com/v1
    description: Production

paths:                   # Endpoints and operations
  /resources: ...

components:              # Reusable definitions
  schemas: ...
  parameters: ...
  responses: ...
  securitySchemes: ...
  requestBodies: ...
  headers: ...

security:                # Global security requirements
  - bearerAuth: []

tags:                    # Logical grouping of operations
  - name: resources
    description: Resource management
```

### Path and Operation Structure

```yaml
paths:
  /resources/{id}:
    parameters:                    # Path-level parameters (shared by all operations)
      - $ref: '#/components/parameters/ResourceId'
    get:
      tags: [resources]
      summary: Get a resource         # Short (< 120 chars)
      description: |                   # Detailed explanation
        Returns a single resource by its unique identifier.
      operationId: getResource         # Unique, used for codegen
      parameters:                      # Operation-specific params
        - $ref: '#/components/parameters/IncludeDeleted'
      responses:
        '200':
          description: Resource found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
              example:
                id: abc-123
                name: Example
        '404':
          $ref: '#/components/responses/NotFound'
```

---

## Schema Design Patterns

### Composition with allOf

Use `allOf` to compose schemas from shared building blocks:

```yaml
schemas:
  BaseResource:
    type: object
    properties:
      id:
        type: string
        format: uuid
      createdAt:
        type: string
        format: date-time
      updatedAt:
        type: string
        format: date-time

  User:
    allOf:
      - $ref: '#/components/schemas/BaseResource'
      - type: object
        required: [email, name]
        properties:
          email:
            type: string
            format: email
          name:
            type: string
```

### Polymorphism with oneOf and Discriminators

Use `oneOf` with `discriminator` for type unions:

```yaml
schemas:
  Notification:
    oneOf:
      - $ref: '#/components/schemas/EmailNotification'
      - $ref: '#/components/schemas/SmsNotification'
      - $ref: '#/components/schemas/PushNotification'
    discriminator:
      propertyName: type
      mapping:
        email: '#/components/schemas/EmailNotification'
        sms: '#/components/schemas/SmsNotification'
        push: '#/components/schemas/PushNotification'

  EmailNotification:
    type: object
    required: [type, to, subject]
    properties:
      type:
        type: string
        enum: [email]
      to:
        type: string
        format: email
      subject:
        type: string
```

### Read vs Write Schemas

Separate schemas for create/update vs read operations:

```yaml
schemas:
  UserCreate:
    type: object
    required: [email, name]
    properties:
      email:
        type: string
        format: email
      name:
        type: string

  UserResponse:
    allOf:
      - $ref: '#/components/schemas/BaseResource'
      - $ref: '#/components/schemas/UserCreate'
```

This avoids clients sending `id`, `createdAt`, or other server-managed fields.

### Pagination Pattern

```yaml
schemas:
  PaginatedResponse:
    type: object
    required: [data, pagination]
    properties:
      data:
        type: array
        items: {}              # Override in specific responses
      pagination:
        $ref: '#/components/schemas/PaginationMeta'

  PaginationMeta:
    type: object
    properties:
      total:
        type: integer
      page:
        type: integer
      perPage:
        type: integer
      totalPages:
        type: integer

parameters:
  PageParam:
    name: page
    in: query
    schema:
      type: integer
      minimum: 1
      default: 1
  PerPageParam:
    name: per_page
    in: query
    schema:
      type: integer
      minimum: 1
      maximum: 100
      default: 20
```

### Enum Patterns

```yaml
# String enum
schemas:
  Status:
    type: string
    enum: [active, inactive, suspended]
    description: |
      - `active` — Resource is live and operational
      - `inactive` — Resource exists but is not in use
      - `suspended` — Resource is temporarily disabled
```

---

## Validation Rules

### Required Fields Checklist

| Element | Required fields |
|---------|----------------|
| `info` | `title`, `version` |
| `paths.{path}.{method}` | `responses` |
| `responses.{code}` | `description` |
| `parameter` | `name`, `in` |
| `schema` (object) | `type`, relevant `properties` |

### Common Validation Rules

| Rule | Description |
|------|-------------|
| Unique `operationId` | Every operation must have a unique ID across the spec |
| Path param coverage | Every `{param}` in a path must have a matching parameter definition |
| No unused components | Every `components/*` entry should be referenced by at least one `$ref` |
| Response completeness | Every operation should have at least one `2xx` and one error response |
| Type consistency | Properties should have explicit `type` (don't rely on inference) |

### Format Validators

Common `format` values and what they validate:

| Format | Type | Validates |
|--------|------|-----------|
| `date-time` | string | ISO 8601 datetime |
| `date` | string | ISO 8601 date |
| `email` | string | RFC 5322 email |
| `uri` | string | RFC 3986 URI |
| `uuid` | string | RFC 4122 UUID |
| `int32` | integer | 32-bit signed integer |
| `int64` | integer | 64-bit signed integer |
| `float` | number | Single precision |
| `double` | number | Double precision |

---

## Code Generation Integration

### Generator Configuration

```yaml
# openapi-generator config
generatorName: typescript-axios
inputSpec: ./openapi.yaml
outputDir: ./generated/client
additionalProperties:
  supportsES6: true
  npmName: "@myorg/api-client"
  withInterfaces: true
```

### Codegen-Friendly Conventions

| Convention | Why it matters |
|-----------|---------------|
| Unique `operationId` | Becomes method name in generated SDKs |
| Consistent casing | Avoids naming conflicts across languages |
| Explicit `type` on all schemas | Prevents codegen ambiguity |
| `$ref` for shared schemas | Generates shared types, not duplicates |
| `enum` with string values | Generates type-safe constants |

---

## Versioning in Specs

### URL-Based Versioning

```yaml
servers:
  - url: https://api.example.com/v1
    description: Version 1 (current)
  - url: https://api.example.com/v2
    description: Version 2 (beta)
```

### Deprecation

```yaml
paths:
  /old-endpoint:
    get:
      deprecated: true
      summary: "[Deprecated] Use /new-endpoint instead"
      description: |
        **Deprecated since v2.3.0.** Will be removed in v3.0.0.
        Use `GET /new-endpoint` instead.
```

### Breaking vs Non-Breaking Changes

| Change type | Breaking? | Example |
|------------|-----------|---------|
| Add optional field | No | New optional query parameter |
| Add new endpoint | No | New path |
| Remove endpoint | Yes | Delete a path |
| Remove field | Yes | Drop a response property |
| Change field type | Yes | String to integer |
| Add required field | Yes | New required request property |
| Rename field | Yes | `userName` to `user_name` |

---

## Reusable Components

### Component Categories

Organize `components` by type for maintainability:

```yaml
components:
  schemas:          # Data models
  parameters:       # Query, path, header params
  responses:        # Standard responses (404, 500, etc.)
  requestBodies:    # Common request payloads
  headers:          # Standard response headers
  securitySchemes:  # Auth mechanisms
  links:            # Hypermedia links between operations
  callbacks:        # Webhook definitions
```

### Standard Error Response

```yaml
components:
  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          description: Machine-readable error code
        message:
          type: string
          description: Human-readable error description
        details:
          type: array
          items:
            $ref: '#/components/schemas/ErrorDetail'

    ErrorDetail:
      type: object
      properties:
        field:
          type: string
        reason:
          type: string
        value: {}

  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    InternalError:
      description: Unexpected server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

---

## Security Scheme Patterns

### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### API Key

```yaml
components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
```

### OAuth 2.0

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read:resources: Read access to resources
            write:resources: Write access to resources
```

### Per-Operation Security Override

```yaml
paths:
  /public/health:
    get:
      security: []       # No auth required (overrides global)
      summary: Health check

  /admin/config:
    put:
      security:
        - bearerAuth: []
        - oauth2: [write:admin]    # Requires elevated scope
```

---

## Examples and Mocking

### Inline Examples

```yaml
schemas:
  User:
    type: object
    properties:
      id:
        type: string
        example: "usr_abc123"
      email:
        type: string
        example: "alice@example.com"
```

### Named Examples (Multiple Scenarios)

```yaml
paths:
  /users/{id}:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                active-user:
                  summary: An active user
                  value:
                    id: usr_abc123
                    email: alice@example.com
                    status: active
                suspended-user:
                  summary: A suspended user
                  value:
                    id: usr_xyz789
                    email: bob@example.com
                    status: suspended
```

### Mock Server

Use examples to power mock servers:

```bash
# Prism (Stoplight) — generates mock responses from examples
prism mock openapi.yaml

# Runs a local server that returns example responses
# matching the schema and status codes in the spec
```
