# Branded Types

**Create nominal types for type safety:**

## Preventing Primitive Mixing

```typescript
// Prevent mixing similar primitive types
type UserId = string & { readonly __brand: 'UserId' };
type PostId = string & { readonly __brand: 'PostId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createPostId(id: string): PostId {
  return id as PostId;
}

function getUser(userId: UserId): User {
  // Implementation
}

const userId = createUserId('user-123');
const postId = createPostId('post-456');

getUser(userId);  // Valid
// getUser(postId);  // Type error: PostId not assignable to UserId
```

## Validation with Branded Types

```typescript
type ValidEmail = string & { readonly __brand: 'ValidEmail' };
type ValidURL = string & { readonly __brand: 'ValidURL' };

function validateEmail(email: string): ValidEmail | null {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email) ? (email as ValidEmail) : null;
}

function sendEmail(to: ValidEmail, subject: string, body: string) {
  // Guaranteed to have valid email
}

const email = validateEmail('user@example.com');
if (email) {
  sendEmail(email, 'Hello', 'World');
}
```

## Benefits

- Compile-time prevention of ID mixing
- Self-documenting code through type names
- Enforced validation at boundaries
- Zero runtime overhead
