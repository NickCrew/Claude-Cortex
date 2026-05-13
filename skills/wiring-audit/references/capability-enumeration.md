# Capability Enumeration

What the capability-side sub-agent looks for in the backend. The goal: build a production registry — every backend capability that *could* be consumed.

Identifier formats must match `surface-enumeration.md` exactly so the diff produces clean matches.

## HTTP route handlers

### Express / Fastify / Koa / Hono

```ts
app.get('/api/users', listUsers)
app.post('/api/users', createUser)
fastify.route({ method: 'PUT', url: '/api/users/:id', handler: updateUser })
hono.delete('/api/users/:id', deleteUser)
```

Capture each as `kind: http_route, identifier: "<METHOD> <path>"`.

Cite the **registration line** (the `app.get(...)` line), not the handler function.

### Next.js Route Handlers (app router)

`app/api/users/route.ts`:

```ts
export async function GET(req: Request) { ... }
export async function POST(req: Request) { ... }
```

Each export is a capability:

- File path becomes the URL: `app/api/users/route.ts` → `/api/users`. Dynamic segments (`[id]`) → `:id`.
- Each exported HTTP method (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) is a separate capability.
- Identifier: `GET /api/users`, `POST /api/users`, etc.
- Cite the **export line** for each method.

### Next.js API Routes (pages router, legacy)

`pages/api/users.ts`:

```ts
export default function handler(req, res) {
  if (req.method === 'GET') { ... }
  else if (req.method === 'POST') { ... }
}
```

Trickier because one file handles multiple methods. Capture each branch as a separate capability:

- Identifier: `GET /api/users` etc.
- Cite the **method check line** (`if (req.method === 'GET')`).

If the handler doesn't check method, capture as `* /api/users` (any method) — the diff will match any consumption URL.

### Response shape

For each route, capture the response shape when inferable:

- Explicit return type: `function listUsers(): Promise<User[]>` → `User[]`.
- `res.json(x)` where `x` is typed: capture x's type.
- Zod/Yup schemas: `res.json(UserListSchema.parse(...))` → schema's inferred type.
- OpenAPI generated handlers: declared response in the schema.

If shape isn't inferable, set `response_shape_source: unknown` and continue. Shape-drift findings only fire when both sides have a known shape.

## tRPC procedures

```ts
export const usersRouter = t.router({
  list: t.procedure.query(({ ctx }) => { ... }),
  create: t.procedure.input(CreateUserInput).mutation(({ input }) => { ... }),
  byId: t.procedure.input(z.object({ id: z.string() })).query(({ input }) => { ... }),
})
```

Capture each procedure:

- Identifier: dotted path from the root router. `users.list`, `users.create`, `users.byId`.
- Method: `query` or `mutation` (captured separately, used for method-drift detection — frontend `useQuery` against backend `mutation` is a finding).
- Cite the procedure definition line.
- Response shape: from the return type inference (procedure return value).
- Auth: if `t.procedure.use(authMiddleware)...`, capture the middleware as the auth signal.

### tRPC type-safety caveat

tRPC catches drift at compile time *if and only if*:

1. Frontend and backend share the same `AppRouter` type.
2. Types regenerate after backend changes (no stale generated client).
3. No `as any` / `@ts-ignore` defeats type checking.

The audit still scans because (a) generated types may be stale, (b) multi-package setups often miss regeneration, (c) escape hatches defeat the type system. tRPC drift findings should note in the suggested fix that "running `pnpm generate-types` (or the project's regen command) may resolve this."

## GraphQL

### Schema-first

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilter): [User!]!
}
type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

Each top-level field is a capability:

- Identifier: `<Type>.<field>` — `Query.user`, `Query.users`, `Mutation.createUser`.
- Cite the field declaration line.
- Response shape: derived from return type.

### Code-first (Nexus, Pothos, TypeGraphQL)

Same shape; cite the field's `.field()` or decorator declaration.

### Resolvers

The resolver implementation is *not* a separate capability — it's the implementation of the schema's field. Cite the schema field, not the resolver.

## Server actions (Next.js)

```ts
'use server'

export async function createUser(formData: FormData) {
  // ...
}
```

- Identifier: function symbol — `createUser`.
- Cite the export line.
- Method: `server-action` (no HTTP method semantics).
- Response shape: from return type.

If the file has `'use server'` at the top, all exported async functions are server actions. Otherwise, only functions with their own `'use server'` directive at the top of their body.

## Exported hooks (when treated as a capability surface)

This is the inverted case — frontend "capability" surfaced via hooks rather than HTTP. Common in component library packages.

```ts
// packages/ui/hooks/index.ts
export function useTheme() { ... }
export function useToast() { ... }
```

Capture as `kind: exported_hook, identifier: <hook-symbol>`. Cite the export line.

The audit will diff against `hook-import` consumption findings — if a component imports `useToast` from `@ui/hooks` but `useToast` isn't exported, that's an orphan-surface finding.

## WebSocket handlers

```ts
io.on('connection', (socket) => {
  socket.on('project:update', handleProjectUpdate)
  socket.on('project:delete', handleProjectDelete)
})
```

Each `socket.on(<event>, ...)` is a capability:

- Identifier: event name — `project:update`, `project:delete`.
- Cite the registration line.

## Environment variables (consumed by backend)

```ts
const stripeKey = process.env.STRIPE_API_KEY
if (!stripeKey) throw new Error(...)
```

Capture as `kind: env_var_consumer, identifier: STRIPE_API_KEY`. Cite the read site.

These are capabilities in the sense that the backend's behavior depends on them. The diff finds **unsurfaced config**: env vars consumed but with no UI/CLI/admin surface to set them, no `.env.example` documentation, no settings panel.

## Config key consumers

```ts
if (config.auth.providers.github.enabled) { ... }
```

Capture as `kind: config_key_consumer, identifier: auth.providers.github.enabled`. Cite the read site.

Same role as env vars — the diff finds keys read but never surfaced to users to control.

## Auth signals

For each capability, capture the auth/permission requirement:

| Pattern | Auth value |
|---|---|
| `if (!session) return 401` | `requires-session` |
| `if (session.user.role !== 'admin') return 403` | `requires-role:admin` |
| `if (params.userId !== session.user.id) return 403` | `requires-self` |
| Middleware applied to route group | the middleware's name |
| No check | `none` |

The diff uses these to detect **permission-drift**: UI shows a button to all users, backend rejects non-admins (or vice versa, UI hides the button but backend doesn't actually enforce).

## What NOT to enumerate

- Internal helper functions called only from within handlers — not exposed.
- Database queries — those are implementation detail, not capability.
- Logging / metrics calls — not capabilities.
- Test fixtures, mocks, dev-only routes (those are sometimes capabilities — flag them with `dev-only: true` so the diff can decide whether to include them).

## Sub-agent prompt seed (capability side)

```
# Mode
Wiring audit — capability side. Enumerate every backend capability the UI could consume.

# Scope
[<backend path or "the entire backend rooted at <path>">]

# Stack signal
[Detected: Express, Next.js route handlers, tRPC, etc.]

# What to find
1. HTTP route definitions (Express, Fastify, Hono, Koa, Next.js route handlers, Next.js API routes).
2. tRPC procedures (router definitions, query/mutation distinction).
3. GraphQL schema fields (Query, Mutation, Subscription top-level fields).
4. Server actions (Next.js 'use server' exports).
5. Exported hooks (when the project has a UI library that exports hooks).
6. WebSocket event handlers.
7. Env var reads (process.env.X usage in backend code).
8. Config key reads.

# Identifier format
- http_route: "<METHOD> <path>" — extract from registration
- trpc_procedure: dotted path from root router
- graphql_field: "<Type>.<field>"
- server_action: function symbol
- exported_hook: hook symbol
- websocket_handler: event name
- env_var_consumer: VAR_NAME
- config_key_consumer: dotted.path

# For each capability, capture
- Identifier (per format above)
- Location (path:line)
- Evidence (verbatim line)
- Response shape (when inferable from types or schemas)
- Auth requirement (or "none")

# Output contract
Return YAML matching the capabilities[] schema in references/audit-protocol.md.

# Important
- The audit relies on identifier format consistency. Verify each identifier follows the format exactly.
- For Next.js dynamic routes ([id], [...slug]), templatize as :id, :*slug.
- For tRPC, the dotted path is from the root router exposed to the client (e.g., appRouter.users.list → "users.list").
- Don't enumerate internal helpers, only exposed capabilities.

# Verification expectation
The orchestrator will verify every citation. Findings whose evidence doesn't match the cited line will be discarded.
```
