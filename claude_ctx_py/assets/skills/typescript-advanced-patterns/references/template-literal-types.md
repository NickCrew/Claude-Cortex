# Template Literal Types

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

## Nested Template Literals

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
