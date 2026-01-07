# Decorators (Stage 3)

**Class and method decorators for cross-cutting concerns:**

## Method Decorators

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
```

## Property Decorators

```typescript
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

## Class Decorators

```typescript
// Class decorator for metadata
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class SealedClass {
  constructor(public name: string) {}
}
```

## Decorator Factories

```typescript
// Decorator with parameters
function component(config: { selector: string }) {
  return function(constructor: Function) {
    constructor.prototype.selector = config.selector;
  };
}

@component({ selector: 'app-user' })
class UserComponent {
  // selector property added at runtime
}
```

## Common Use Cases

- **Logging**: Automatic method call logging
- **Validation**: Property value validation
- **Memoization**: Cache method results
- **Authorization**: Check permissions before execution
- **Dependency Injection**: Inject dependencies into classes
- **Metadata**: Attach runtime metadata for frameworks
