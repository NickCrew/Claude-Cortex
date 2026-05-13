# Surface Enumeration

What the surface-side sub-agent looks for in the UI. The goal: build a consumption registry — every place the UI calls into a backend capability.

The audit's diff key is `(kind, identifier)`. Every consumption must produce both with stable formatting.

## Generic patterns (any UI framework)

### HTTP calls

Look for these call patterns and capture the URL + method + location:

| Pattern | Example |
|---|---|
| `fetch()` | `fetch('/api/users', { method: 'POST', body })` |
| `axios.*` | `axios.get('/api/users/' + id)` |
| Custom wrapper | `api.users.list()`, `client.post(...)` — follow the wrapper to the underlying URL |
| `XMLHttpRequest` | `xhr.open('POST', '/api/...')` |

For each HTTP consumption:

- **Identifier**: `<METHOD> <path-template>`. Templatize concrete IDs back to `:param` form when the URL is built from string concatenation or template literals (e.g., ``fetch(`/api/users/${id}`)`` becomes `GET /api/users/:id`).
- **Location**: cite the call site (the `fetch` line), not the import.
- **Evidence**: verbatim call line.
- **Response shape**: if the response is consumed (e.g., `const data = await res.json()` → `data.foo`), capture the access pattern as `{ foo: unknown }`. If TypeScript types are present (`fetch<User>(...)` or generated client), capture the declared shape.

### Form submissions

`<form action="/api/users" method="post">` or `<form onSubmit={...}>` with a fetch in the handler. Capture as HTTP consumption with the form action + method.

### WebSocket connections

`new WebSocket('/ws/...')`, `socket.io-client`. Capture the URL or topic/event name as identifier.

### Environment variables and config

`process.env.X` reads in client code (Next.js: `NEXT_PUBLIC_*`). Capture as `kind: env-var, identifier: NEXT_PUBLIC_X`. Config file reads in client code: `config.foo.bar` capture as `kind: config-key, identifier: foo.bar`.

## React-specific patterns

(See `react-patterns.md` for the deep dive. Summary here.)

### Hooks

Both *imported hooks* and *hook usage* count as surface consumption signals.

- **Imported hook** (`import { useUsers } from '@/hooks/users'`): capture as `kind: hook-import, identifier: useUsers`. The diff matches against an exported_hook capability.
- **Hook call** (`const { data } = useUsers()`): also a consumption — but if the call doesn't go via an imported hook (it's defined inline), capture the inner call (e.g., the `fetch` inside).

### React Query / SWR / Apollo

```ts
useQuery({ queryKey: ['users', id], queryFn: () => fetch('/api/users/' + id) })
useMutation({ mutationFn: (body) => fetch('/api/users', { method: 'POST', body: JSON.stringify(body) }) })
useSWR('/api/users')
```

Surface the inner `fetch` (or fetcher function) as the HTTP consumption. The query key isn't the identifier; the URL is.

### tRPC client

```ts
trpc.users.list.useQuery()
trpc.users.create.useMutation()
trpc.users.byId.useQuery({ id })
```

Capture as `kind: trpc, identifier: <dotted path>` — `users.list`, `users.create`, `users.byId`.

The dotted path is the diff key. Method (query vs mutation) is captured separately; tRPC procedures are typed as `query` or `mutation` and a frontend `useQuery` against a backend `mutation` is a method-drift finding.

### GraphQL

```ts
const { data } = useQuery(USER_QUERY)
gql`query Foo { user(id: $id) { name email } }`
```

Capture as `kind: graphql, identifier: <Type>.<field>`. For multi-field queries, emit one consumption per top-level field.

### Server actions (Next.js)

```ts
'use server'
export async function createUser(formData: FormData) { ... }

// elsewhere
<form action={createUser}>
```

The *call site* (`<form action={createUser}>` or `await createUser(...)`) is a consumption with `kind: server-action, identifier: createUser`. The function definition is a capability — the capability enumerator handles that side.

### React Router / Next.js routing

Routing itself is a UI surface, not a consumption — but route loaders/actions can be consumptions:

```ts
export async function loader({ params }) {
  return fetch(`/api/users/${params.id}`)
}
```

Surface the inner `fetch` as the consumption. The route definition (`path: "/users/:id"`) is a UI surface but doesn't itself consume anything; only its loader/action does.

## Permission signals

When a consumption is gated by a permission check at the call site, capture:

```ts
if (user.role === 'admin') {
  return fetch('/api/admin/audit')
}
```

→ `permission_signal: "user.role === 'admin'"`

Used by the diff to detect permission-drift (e.g., UI requires admin, backend has no auth check).

## User labels

For surfaces that have user-visible text (buttons, links, menu items, headings), capture the label string:

```ts
<button onClick={() => deleteUser(id)}>Delete account</button>
```

→ `user_label: "Delete account"`

Used by the stale-label detection pass to find labels that reference renamed backend concepts.

## What NOT to enumerate

- Pure styling — no consumption.
- Internal state mutations (`setX(y)`) — no consumption.
- React Query cache reads (`queryClient.getQueryData(...)`) — these are derived; capture the *original* fetcher.
- Imports of pure types or constants — not consumption (no runtime call).
- Third-party SDK calls (Stripe.js, Auth0, etc.) — those are integrations, captured as `kind: http` only if you want to audit drift against your own backend's mirror of those concepts.

## Custom hook unwrapping

When a component calls a custom hook that wraps backend calls:

```ts
// hooks/users.ts
export function useUsers() {
  return useQuery({ queryKey: ['users'], queryFn: () => fetch('/api/users') })
}

// components/UserList.tsx
function UserList() {
  const { data } = useUsers()    // ← surface, consumes useUsers
}
```

Two records:

1. The component's `useUsers()` call — `kind: hook-import, identifier: useUsers`. Diffs against the exported_hook capability.
2. The hook's inner `fetch('/api/users')` — `kind: http, identifier: GET /api/users`. Diffs against the http_route capability.

Both must be captured. Components surface to hooks; hooks surface to backend. The audit checks both layers.

## Sub-agent prompt seed (surface side)

```
# Mode
Wiring audit — surface side. Enumerate every UI consumption.

# Scope
[<UI path or "the entire frontend rooted at <path>">]

# Stack signal
[Detected: React + react-query + tRPC + Next.js, etc.]

# What to find
1. HTTP calls (fetch, axios, custom wrappers) — capture URL + method.
2. tRPC client calls (trpc.x.y.useQuery / .useMutation / .query / .mutate).
3. GraphQL queries (useQuery, gql tags) — top-level field per consumption.
4. Server action call sites (form action + direct calls).
5. WebSocket connections.
6. Hook imports (custom hooks wrapping backend calls).
7. Form submissions to backend routes.
8. Permission-gated calls — capture the gating expression.
9. User-visible labels (buttons, links, menu items) — capture the label text.
10. Env var reads (process.env.X) and config-key reads in client code.

# Identifier format
- HTTP: "<METHOD> <path-template>" — templatize :params
- tRPC: dotted path
- GraphQL: <Type>.<field>
- Server action: function symbol
- Hook: hook symbol
- WebSocket: event/topic
- Env var: VAR_NAME
- Config key: dotted.path

# Output contract
Return YAML matching the surfaces[] schema in references/audit-protocol.md.

# Important
- For absence claims (e.g., "this component has no consumption") — only assert if you've thoroughly reviewed the file.
- Capture user_label for any element with visible text — used downstream for stale-label detection.
- Custom hooks: capture BOTH the hook-import consumption AND any inner consumptions inside the hook definition.

# Verification expectation
The orchestrator will verify every citation. Findings whose evidence doesn't match the cited line will be discarded. Optimize for accuracy.
```
