# Testing Type-Safe Code

## Type Assertion Tests

```typescript
// Type equality checker
type AssertEqual<T, U> = T extends U ? (U extends T ? true : false) : false;

type Test1 = AssertEqual<Pick<User, 'name'>, { name: string }>;  // true
type Test2 = AssertEqual<string, number>;  // false
```

## Compile-Time Validation

```typescript
// Expect type to match
function expectType<T>(value: T): T {
  return value;
}

const user: User = { id: 1, name: 'John', email: 'john@example.com', password: 'secret' };
expectType<UserResponse>(user);  // Error: password should not exist
```

## Test Helper Types

```typescript
// Assert never (for exhaustiveness checking)
type AssertNever<T extends never> = T;

// Assert extends
type AssertExtends<T, U extends T> = U;

// Assert assignable
type AssertAssignable<T, U> = U extends T ? true : false;
```

## Runtime Type Testing

```typescript
import { expectType, expectError, expectAssignable } from 'tsd';

// Test type inference
const result = identity(42);
expectType<number>(result);

// Test error cases
// @ts-expect-error
expectError(getUser('invalid-id'));

// Test assignability
interface Base { id: number; }
interface Extended extends Base { name: string; }

expectAssignable<Base>({} as Extended);
```

## Property-Based Type Testing

```typescript
// Test all properties of a type
type TestUserProperties = {
  [K in keyof User]: User[K] extends string | number ? true : false;
};

// Ensure required properties exist
type RequiredFields = Required<Pick<User, 'id' | 'name' | 'email'>>;
```

## Testing Discriminated Unions

```typescript
type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: string };

// Test exhaustiveness
function testExhaustive(state: State) {
  switch (state.status) {
    case 'idle':
    case 'loading':
    case 'success':
      return;
    default:
      // Should be never
      const _exhaustive: never = state;
      return _exhaustive;
  }
}
```

## Type Coverage Tools

Use `type-coverage` to ensure high type safety:

```bash
npm install --save-dev type-coverage

# Check type coverage
npx type-coverage

# Require 100% coverage
npx type-coverage --at-least 100
```

## Testing Frameworks

- **tsd**: Test TypeScript type definitions
- **dtslint**: Linter for .d.ts files
- **type-coverage**: Measure type coverage percentage
- **ts-expect**: Runtime type checking for tests
