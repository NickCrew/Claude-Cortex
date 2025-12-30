# Common Pitfalls

## Type Assertions vs Type Guards

```typescript
// Bad - unsafe type assertion
const value = input as string;

// Good - safe type guard
function assertString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Not a string');
  }
}

assertString(input);
// input is now narrowed to string
```

## Any vs Unknown

```typescript
// Bad - loses type safety
function process(data: any) {
  return data.toUpperCase();  // No type checking
}

// Good - maintains type safety
function processUnknown(data: unknown) {
  if (typeof data === 'string') {
    return data.toUpperCase();  // Type guard required
  }
  throw new Error('Expected string');
}
```

## Overusing Generics

```typescript
// Bad - unnecessary complexity
function add<T extends number, U extends number>(a: T, b: U): number {
  return a + b;
}

// Good - simple and clear
function add(a: number, b: number): number {
  return a + b;
}
```

## Incorrect Type Narrowing

```typescript
// Bad - doesn't narrow type
function isString(value: any): boolean {
  return typeof value === 'string';
}

// Good - properly narrows type
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
```

## Forgetting Readonly

```typescript
// Bad - mutable when should be immutable
interface Config {
  apiUrl: string;
  timeout: number;
}

// Good - prevent accidental mutations
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}
```

## Enum Pitfalls

```typescript
// Bad - numeric enums allow invalid values
enum Status {
  Active,
  Inactive
}

const status: Status = 999;  // Valid but meaningless

// Good - use string enums or const objects
enum Status {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}

// Or use const object with as const
const Status = {
  Active: 'ACTIVE',
  Inactive: 'INACTIVE'
} as const;
```

## Not Using Strict Mode

```typescript
// Always enable in tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictPropertyInitialization": true
  }
}
```

## Type vs Interface Confusion

```typescript
// Use type for unions, intersections, utilities
type ID = string | number;
type Point = { x: number } & { y: number };

// Use interface for object shapes that may be extended
interface User {
  id: ID;
  name: string;
}

interface Admin extends User {
  permissions: string[];
}
```
