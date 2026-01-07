# Utility Types Composition

**Combine utility types for complex transformations:**

## Deep Transformations

```typescript
// Deep partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Make specific keys required
type RequireKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

interface User {
  id?: number;
  name?: string;
  email?: string;
}

type UserWithId = RequireKeys<User, 'id'>;
// { id: number; name?: string; email?: string }
```

## Function Type Utilities

```typescript
// Extract function parameter types
type Parameters<T extends (...args: any[]) => any> =
  T extends (...args: infer P) => any ? P : never;

function processUser(id: number, name: string): void {}

type ProcessUserParams = Parameters<typeof processUser>;
// [number, string]

// Extract return type
type ReturnType<T extends (...args: any[]) => any> =
  T extends (...args: any[]) => infer R ? R : never;
```

## Advanced Transformations

```typescript
// Flatten nested types
type Flatten<T> = T extends any[] ? T[number] : T;

type Nested = (string | number)[][];
type Flat = Flatten<Nested>;  // (string | number)[]

// Exclude nullable values
type NonNullable<T> = T extends null | undefined ? never : T;

// Recursive type definitions
type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };
```

## Readonly Utilities

```typescript
// Deep readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object
    ? DeepReadonly<T[P]>
    : T[P];
};

// Mutable (remove readonly)
type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};
```

## Key Manipulation

```typescript
// Extract keys of specific type
type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

interface Example {
  name: string;
  age: number;
  active: boolean;
  count: number;
}

type StringKeys = KeysOfType<Example, string>;  // 'name'
type NumberKeys = KeysOfType<Example, number>;  // 'age' | 'count'
```
