# Performance Best Practices

## Avoid Excessive Type Complexity

**Keep types simple and composable:**

```typescript
// Bad - deeply nested types
type Complex<T> = T extends Array<infer U>
  ? U extends Array<infer V>
    ? V extends Array<infer W>
      ? W extends Array<infer X>
        ? X
        : never
      : never
    : never
  : never;

// Good - iterative approach
type ElementType<T> = T extends (infer E)[] ? E : T;

type Deep1<T> = ElementType<T>;
type Deep2<T> = ElementType<Deep1<T>>;
```

## Use Type Aliases for Reusability

**Extract common patterns:**

```typescript
// Define once, reuse everywhere
type ID = string | number;
type Timestamp = number;
type Optional<T> = T | null | undefined;

interface User {
  id: ID;
  createdAt: Timestamp;
  lastLogin: Optional<Timestamp>;
}
```

## Leverage Inference

**Let TypeScript infer when possible:**

```typescript
// Don't over-annotate
const users = [
  { id: 1, name: 'John' },
  { id: 2, name: 'Jane' }
];  // Type inferred automatically

// Use inference in generics
function identity<T>(value: T): T {
  return value;
}

const num = identity(42);  // T inferred as 42 (literal type)
```

## Avoid Type Computation Overhead

```typescript
// Bad - expensive type computation on every use
type ExpensiveUnion<T> = T extends any
  ? { [K in keyof T]: SomeComplexType<T[K]> }
  : never;

// Good - compute once, reuse
type PrecomputedType = ExpensiveUnion<MyType>;
function useType(value: PrecomputedType) { }
```

## Use Index Signatures Wisely

```typescript
// Bad - loses type safety
interface LooseMap {
  [key: string]: any;
}

// Good - constrained types
interface TypedMap {
  [key: string]: string | number;
}

// Better - use Record for known types
type StrictMap = Record<'id' | 'name' | 'age', string | number>;
```

## Optimize Union Types

```typescript
// Bad - large union causes slow checking
type ManyStrings = 'a' | 'b' | 'c' | /* ...100 more */ | 'z';

// Good - use branded types or enums for large sets
enum StringEnum {
  A = 'a',
  B = 'b',
  // ...
}
```
