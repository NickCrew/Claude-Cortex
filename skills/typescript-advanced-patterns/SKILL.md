---
name: typescript-advanced-patterns
description: Advanced TypeScript patterns for type-safe, maintainable code using sophisticated type system features. Use when building type-safe APIs, implementing complex domain models, or leveraging TypeScript's advanced type capabilities.
---

# TypeScript Advanced Patterns

Expert guidance for leveraging TypeScript's advanced type system features to build robust, type-safe applications with sophisticated type inference, compile-time guarantees, and maintainable domain models.

## When to Use This Skill

- Building type-safe APIs with strict contracts and validation
- Implementing complex domain models with compile-time enforcement
- Creating reusable libraries with sophisticated type inference
- Enforcing business rules through the type system
- Building type-safe state machines and builders
- Developing framework integrations requiring advanced types
- Implementing runtime validation with type-level guarantees

## Core Patterns

### 1. Conditional Types

**Type selection based on conditions:**
```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false

// Extract function return types
type ReturnTypeOf<T> = T extends (...args: any[]) => infer R ? R : never;

type Fn = () => { name: string; age: number };
type Result = ReturnTypeOf<Fn>;  // { name: string; age: number }

// Extract array element types
type ElementOf<T> = T extends (infer E)[] ? E : never;

type Items = ElementOf<string[]>;  // string
```

**Use cases:**
- Type transformation and extraction
- Conditional API responses based on request types
- Generic utility type creation
- Framework integration types

### 2. Mapped Types

**Transform object types systematically:**
```typescript
// Make all properties optional
type Partial<T> = {
  [P in keyof T]?: T[P];
};

// Make all properties readonly
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

// Pick specific properties
type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

// Create API response type
type UserResponse = Omit<User, 'password'>;

// Create update type (all optional)
type UserUpdate = Partial<User>;

// Create creation type (no id)
type UserCreate = Omit<User, 'id'>;
```

**Advanced mapping:**
```typescript
// Add prefix to all keys
type Prefixed<T, Prefix extends string> = {
  [K in keyof T as `${Prefix}${string & K}`]: T[K];
};

type Events = {
  click: MouseEvent;
  focus: FocusEvent;
};

type Handlers = Prefixed<Events, 'on'>;
// { onclick: MouseEvent; onfocus: FocusEvent }
```

### 3. Template Literal Types

**String type manipulation at compile time:**
```typescript
// Event handler types
type EventNames = 'click' | 'focus' | 'blur';
type EventHandlers = `on${Capitalize<EventNames>}`;
// 'onClick' | 'onFocus' | 'onBlur'

// URL path types
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Endpoint = `/api/${'users' | 'posts' | 'comments'}`;
type Route = `${HTTPMethod} ${Endpoint}`;
// 'GET /api/users' | 'POST /api/users' | ...

// CSS property types
type CSSUnit = 'px' | 'em' | 'rem' | '%';
type Size = `${number}${CSSUnit}`;

const width: Size = '100px';  // Valid
const height: Size = '2em';   // Valid
// const invalid: Size = '100';  // Error
```

**Nested template literals:**
```typescript
type DeepKey<T> = T extends object
  ? {
      [K in keyof T & string]: K | `${K}.${DeepKey<T[K]>}`;
    }[keyof T & string]
  : never;

interface Config {
  database: {
    host: string;
    port: number;
    credentials: {
      username: string;
      password: string;
    };
  };
}

type ConfigKeys = DeepKey<Config>;
// 'database' | 'database.host' | 'database.port' |
// 'database.credentials' | 'database.credentials.username' | ...
```

### 4. Type Guards

**Runtime type checking with type narrowing:**
```typescript
// Basic type guard
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// Discriminated union guard
interface Success {
  status: 'success';
  data: string;
}

interface Error {
  status: 'error';
  message: string;
}

type Result = Success | Error;

function isSuccess(result: Result): result is Success {
  return result.status === 'success';
}

function handleResult(result: Result) {
  if (isSuccess(result)) {
    console.log(result.data);  // Type narrowed to Success
  } else {
    console.log(result.message);  // Type narrowed to Error
  }
}
```

**Generic type guards:**
```typescript
function isArrayOf<T>(
  value: unknown,
  check: (item: unknown) => item is T
): value is T[] {
  return Array.isArray(value) && value.every(check);
}

const data: unknown = [1, 2, 3];

if (isArrayOf(data, (x): x is number => typeof x === 'number')) {
  data.forEach(n => n.toFixed(2));  // Type: number[]
}
```

### 5. Discriminated Unions

**Type-safe state machines and variants:**
```typescript
// State machine with exhaustive checking
type LoadingState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: string[] }
  | { status: 'error'; error: Error };

function renderState(state: LoadingState): string {
  switch (state.status) {
    case 'idle':
      return 'Not started';
    case 'loading':
      return 'Loading...';
    case 'success':
      return `Loaded ${state.data.length} items`;
    case 'error':
      return `Error: ${state.error.message}`;
  }
  // Exhaustiveness checking ensures all cases handled
}
```

**Complex discriminated unions:**
```typescript
// API action types
type Action =
  | { type: 'FETCH_USER'; payload: { userId: string } }
  | { type: 'UPDATE_USER'; payload: { userId: string; data: Partial<User> } }
  | { type: 'DELETE_USER'; payload: { userId: string } }
  | { type: 'CLEAR_USERS' };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_USER':
      // action.payload is { userId: string }
      return { ...state, loading: true };
    case 'UPDATE_USER':
      // action.payload is { userId: string; data: Partial<User> }
      return updateUser(state, action.payload);
    case 'DELETE_USER':
      return deleteUser(state, action.payload.userId);
    case 'CLEAR_USERS':
      // action has no payload
      return { ...state, users: [] };
  }
}
```

## Advanced Patterns

### 6. Branded Types

**Create nominal types for type safety:**
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

**Branded types for validation:**
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

### 7. Builder Pattern with Types

**Type-safe fluent APIs:**
```typescript
interface QueryBuilder<TSelect = unknown, TWhere = unknown> {
  select<T>(): QueryBuilder<T, TWhere>;
  where<T>(): QueryBuilder<TSelect, T>;
  execute(): TSelect extends unknown ? never : Promise<TSelect[]>;
}

// Usage ensures select() called before execute()
const results = await query
  .select<User>()
  .where<{ age: number }>()
  .execute();  // Type: Promise<User[]>

// query.execute();  // Error: select() not called
```

**Progressive builder types:**
```typescript
interface ConfigBuilder<
  THost extends string | undefined = undefined,
  TPort extends number | undefined = undefined
> {
  host: THost;
  port: TPort;

  withHost<H extends string>(host: H): ConfigBuilder<H, TPort>;
  withPort<P extends number>(port: P): ConfigBuilder<THost, P>;

  build: THost extends string
    ? TPort extends number
      ? () => { host: THost; port: TPort }
      : never
    : never;
}

const config = new ConfigBuilder()
  .withHost('localhost')
  .withPort(3000)
  .build();  // Valid

// new ConfigBuilder().build();  // Error: host and port required
```

### 8. Advanced Generics

**Generic constraints and inference:**
```typescript
// Constrain to objects with specific keys
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: 'John', age: 30 };
const name = getProperty(user, 'name');  // Type: string
// const invalid = getProperty(user, 'invalid');  // Error

// Multiple constraints
function merge<T extends object, U extends object>(
  obj1: T,
  obj2: U
): T & U {
  return { ...obj1, ...obj2 };
}
```

**Higher-kinded types pattern:**
```typescript
// Type-safe data structures
interface Functor<F> {
  map<A, B>(fa: F extends { value: any } ? F : never, f: (a: A) => B): any;
}

interface Box<T> {
  value: T;
}

const boxFunctor: Functor<Box<any>> = {
  map<A, B>(fa: Box<A>, f: (a: A) => B): Box<B> {
    return { value: f(fa.value) };
  }
};
```

### 9. Utility Types Composition

**Combine utility types for complex transformations:**
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

// Extract function parameter types
type Parameters<T extends (...args: any[]) => any> =
  T extends (...args: infer P) => any ? P : never;

function processUser(id: number, name: string): void {}

type ProcessUserParams = Parameters<typeof processUser>;
// [number, string]
```

### 10. Type Inference Techniques

**Leverage TypeScript's type inference:**
```typescript
// Infer from function implementation
function createAction<T extends string, P>(
  type: T,
  payload: P
) {
  return { type, payload };
}

const action = createAction('UPDATE_USER', { id: 1, name: 'John' });
// Type: { type: 'UPDATE_USER'; payload: { id: number; name: string } }

// Infer generic types from usage
function useState<S>(
  initialState: S | (() => S)
): [S, (newState: S) => void] {
  // Implementation
}

const [count, setCount] = useState(0);  // S inferred as number
const [user, setUser] = useState({ name: 'John' });  // S inferred as { name: string }
```

**Const assertions for literal types:**
```typescript
// Without const assertion
const colors1 = ['red', 'green', 'blue'];
// Type: string[]

// With const assertion
const colors2 = ['red', 'green', 'blue'] as const;
// Type: readonly ['red', 'green', 'blue']

// Narrow object types
const config = {
  endpoint: '/api/users',
  method: 'GET'
} as const;
// Type: { readonly endpoint: '/api/users'; readonly method: 'GET' }

// Use in discriminated unions
type Action =
  | ReturnType<typeof createAction<'INCREMENT'>>
  | ReturnType<typeof createAction<'DECREMENT'>>;
```

### 11. Decorators (Stage 3)

**Class and method decorators for cross-cutting concerns:**
```typescript
// Method decorator for logging
function log(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
) {
  const original = descriptor.value;

  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    const result = original.apply(this, args);
    console.log(`Result:`, result);
    return result;
  };

  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}

// Property decorator for validation
function validate(validator: (value: any) => boolean) {
  return function(target: any, propertyKey: string) {
    let value = target[propertyKey];

    Object.defineProperty(target, propertyKey, {
      get: () => value,
      set: (newValue) => {
        if (!validator(newValue)) {
          throw new Error(`Invalid value for ${propertyKey}`);
        }
        value = newValue;
      }
    });
  };
}

class User {
  @validate(email => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
  email: string;
}
```

### 12. Advanced Type Manipulation

**Complex type transformations:**
```typescript
// Flatten nested types
type Flatten<T> = T extends any[] ? T[number] : T;

type Nested = (string | number)[][];
type Flat = Flatten<Nested>;  // (string | number)[]

// Exclude nullable values
type NonNullable<T> = T extends null | undefined ? never : T;

// Create function overload types
type Overload<T> = T extends {
  (...args: infer A1): infer R1;
  (...args: infer A2): infer R2;
}
  ? ((...args: A1) => R1) & ((...args: A2) => R2)
  : never;

// Recursive type definitions
type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

function parseJSON(json: string): JSONValue {
  return JSON.parse(json);
}
```

## Performance Best Practices

### 1. Avoid Excessive Type Complexity

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

### 2. Use Type Aliases for Reusability

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

### 3. Leverage Inference

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

## Common Pitfalls

### 1. Type Assertions vs Type Guards

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

### 2. Any vs Unknown

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

### 3. Overusing Generics

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

## Testing Type-Safe Code

**Use type-level tests:**
```typescript
// Type assertion tests
type AssertEqual<T, U> = T extends U ? (U extends T ? true : false) : false;

type Test1 = AssertEqual<Pick<User, 'name'>, { name: string }>;  // true

// Compile-time validation
function expectType<T>(value: T): T {
  return value;
}

const user: User = { id: 1, name: 'John', email: 'john@example.com', password: 'secret' };
expectType<UserResponse>(user);  // Error: password should not exist
```

## Resources

- **TypeScript Handbook**: https://www.typescriptlang.org/docs/handbook/
- **Type Challenges**: https://github.com/type-challenges/type-challenges
- **DefinitelyTyped**: Type definitions for JavaScript libraries
- **ts-toolbelt**: Advanced type utilities library
- **zod**: Runtime validation with TypeScript inference
- **Effect-TS**: Functional programming patterns with advanced types

## Best Practices Summary

1. Use conditional types for type transformation and extraction
2. Leverage mapped types for systematic object type manipulation
3. Create template literal types for string-based type safety
4. Implement type guards for runtime type checking with narrowing
5. Design discriminated unions for exhaustive state handling
6. Apply branded types to prevent mixing similar primitives
7. Build type-safe fluent APIs with progressive builder types
8. Use generic constraints to enforce type relationships
9. Compose utility types for complex transformations
10. Leverage const assertions for literal type inference
11. Keep type complexity manageable and composable
12. Prefer unknown over any for type-safe error handling
