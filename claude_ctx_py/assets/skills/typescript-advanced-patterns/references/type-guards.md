# Type Guards

**Runtime type checking with type narrowing:**

## Basic Type Guards

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

## Generic Type Guards

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

## Assertion Functions

```typescript
// Type assertion function
function assertString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Not a string');
  }
}

const input: unknown = 'hello';
assertString(input);
// input is now narrowed to string
input.toUpperCase();  // Valid
```
