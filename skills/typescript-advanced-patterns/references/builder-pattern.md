# Builder Pattern with Types

**Type-safe fluent APIs:**

## Query Builder Example

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

## Progressive Builder Types

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

## Type State Pattern

```typescript
// Enforce method call order at compile time
interface EmptyBuilder {
  addItem<T>(item: T): FilledBuilder<T>;
}

interface FilledBuilder<T> {
  addItem(item: T): FilledBuilder<T>;
  build(): T[];
}

// Must call addItem() before build()
const items = builder
  .addItem('first')
  .addItem('second')
  .build();  // Valid

// builder.build();  // Error: can't build empty
```
