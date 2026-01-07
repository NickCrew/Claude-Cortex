# API Contract Validation

**Goal:** Ensure seamless integration between frontend skills/components and backend APIs.

## Strategy

1.  **Schema-First Design:** Define the API contract *before* implementing the UI.
2.  **Validation:** Use runtime validation (Zod, Io-TS) to ensure incoming data matches the contract.
3.  **Mocking:** Generate strict mocks based on the schema for development.

## Implementation Pattern

### 1. Define Schema (Zod)
```typescript
import { z } from 'zod';

export const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(2),
  role: z.enum(['admin', 'user']),
  preferences: z.record(z.boolean()).optional()
});

export type User = z.infer<typeof UserSchema>;
```

### 2. Validation Hook
```typescript
function useUser(id: string) {
  return useQuery(['user', id], async () => {
    const data = await fetch(`/api/users/${id}`).then(r => r.json());
    // Runtime validation - throws if contract is violated
    return UserSchema.parse(data);
  });
}
```

### 3. Contract Tests
- Write integration tests that verify the UI handles both success states (valid data) and contract violations (invalid data/error boundaries) gracefully.
