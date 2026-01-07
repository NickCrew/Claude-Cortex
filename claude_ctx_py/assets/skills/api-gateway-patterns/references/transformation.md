# Request/Response Transformation

Gateway-level request and response transformation patterns for API adaptation and normalization.

## Request Transformation

**Implementation Pattern:**
```javascript
// Envoy Lua filter / Kong plugin pattern
function transform_request(request)
  -- Add correlation ID
  request.headers["X-Correlation-ID"] = generate_uuid()

  -- Transform body structure
  local body = json.decode(request.body)
  body.metadata = {
    timestamp: current_time(),
    source: request.headers["User-Agent"]
  }
  request.body = json.encode(body)

  -- Normalize headers
  request.headers["X-Forwarded-For"] = request.remote_addr
end
```

**Use Cases:**
- Header injection/normalization
- Body structure transformation
- Legacy API adaptation
- Adding metadata

## Response Transformation

**Implementation Pattern:**
```javascript
function transform_response(response)
  -- Remove sensitive fields
  local body = json.decode(response.body)
  body.internal_id = nil
  body.database_metadata = nil

  -- Add pagination metadata
  response.headers["X-Total-Count"] = body.total
  response.headers["X-Page-Size"] = body.page_size

  response.body = json.encode(body)
end
```

**Benefits:**
- Security (filter sensitive data)
- Consistency (standardized responses)
- Client optimization (field filtering)
