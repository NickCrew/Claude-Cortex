# Mapped Types

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

## Advanced Mapping

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
