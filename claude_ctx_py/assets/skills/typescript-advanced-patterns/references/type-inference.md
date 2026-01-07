# Type Inference Techniques

**Leverage TypeScript's type inference:**

## Const Assertions

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
```

## Inference from Implementation

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
```

## Inference with Generics

```typescript
// Let TypeScript infer generic types
function identity<T>(value: T): T {
  return value;
}

const num = identity(42);  // T inferred as 42 (literal type)
const str = identity('hello');  // T inferred as 'hello'

// Inference from array methods
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);  // Type: number[]
```

## Discriminated Union Inference

```typescript
// Use in discriminated unions
type Action =
  | ReturnType<typeof createAction<'INCREMENT'>>
  | ReturnType<typeof createAction<'DECREMENT'>>;

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'INCREMENT':
      return state + 1;
    case 'DECREMENT':
      return state - 1;
  }
}
```

## Tuple Inference

```typescript
// Infer tuple types
function tuple<T extends any[]>(...args: T): T {
  return args;
}

const pair = tuple(1, 'hello');  // Type: [number, string]
const triple = tuple(1, 'hello', true);  // Type: [number, string, boolean]
```

## Contextual Typing

```typescript
// Type inferred from context
interface Point {
  x: number;
  y: number;
}

const points: Point[] = [
  { x: 0, y: 0 },  // Type inferred from array type
  { x: 1, y: 1 }
];

// Callback inference
['1', '2', '3'].map(str => parseInt(str));  // str inferred as string
```
