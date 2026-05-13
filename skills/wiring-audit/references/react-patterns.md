# React Patterns

The signal catalog for React-side surface enumeration. The audit is generic across UI frameworks, but in practice React is the common case — and React's patterns have unique pitfalls (custom hooks hide URLs, server components blur FE/BE, tRPC's type-safety can mislead).

## Data layer signals

### Plain `fetch` and `axios`

Direct calls. Easiest to detect.

```tsx
const data = await fetch('/api/users').then(r => r.json())
const { data } = await axios.get('/api/users/' + id)
```

Capture the URL via templatization (`/api/users/:id`).

### React Query (TanStack Query)

```tsx
const { data, isLoading } = useQuery({
  queryKey: ['users', id],
  queryFn: () => fetch('/api/users/' + id).then(r => r.json()),
})

const mutation = useMutation({
  mutationFn: (input: NewUser) => fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify(input),
  }),
})
```

The `queryFn` / `mutationFn` is where the consumption lives. Capture the inner fetch.

**Caveat:** when fetchers are wrapped (`fetcher(url)`), follow the wrapper to find the underlying URL. If the wrapper is sufficiently dynamic that you can't templatize, mark `confidence: low`.

### SWR

```tsx
const { data } = useSWR('/api/users', fetcher)
```

The first arg is the URL (often the cache key too). Capture as `GET <url>`.

### Apollo Client / urql (GraphQL)

```tsx
const QUERY = gql`
  query GetUser($id: ID!) {
    user(id: $id) { name email }
  }
`
const { data } = useQuery(QUERY, { variables: { id } })
```

Capture each top-level field as `kind: graphql, identifier: Query.user`. Sub-fields (`user.name`, `user.email`) get captured as the `response_shape`.

### tRPC client

```tsx
const { data } = trpc.users.byId.useQuery({ id })
const create = trpc.users.create.useMutation()
await create.mutateAsync(newUser)
```

Capture as `kind: trpc, identifier: users.byId` / `users.create`. Method captured separately:
- `.useQuery` / `.query` → method `query`
- `.useMutation` / `.mutate` / `.mutateAsync` → method `mutation`

**Type-safety caveat:** tRPC catches procedure renames at compile time *only if*:
- Frontend imports the *current* `AppRouter` type from the backend (no stale generated client).
- Both sides type-check successfully (`tsc --noEmit` passes).
- No `as any`, `@ts-ignore`, or `<any>` cast in the call site.

In real codebases, all three are routinely violated:
- Multi-package monorepos miss the regen step.
- Pre-commit type-check is sometimes skipped.
- Generated client packages get out of sync with backend types.

The audit still scans tRPC consumption because the type-check might be lying.

## Custom hook unwrapping

Most React apps have a hook layer between components and fetchers:

```ts
// hooks/users.ts
export function useUsers() {
  return useQuery({ queryKey: ['users'], queryFn: () => fetch('/api/users') })
}

// components/UserList.tsx
function UserList() {
  const { data } = useUsers()
}
```

**Two consumptions to capture:**

1. **Hook-import**: `UserList` consumes `useUsers` (`kind: hook-import, identifier: useUsers`). Diffs against an `exported_hook` capability.
2. **Inner consumption**: `useUsers`'s `fetch('/api/users')` (`kind: http, identifier: GET /api/users`). Diffs against an `http_route` capability.

The audit's diff treats these as separate findings. A component that imports a hook that doesn't exist is one bug; a hook that fetches a URL that doesn't exist is another.

## Next.js patterns

### Route handlers (app router)

```ts
// app/api/users/route.ts
export async function GET(req: Request) { ... }
export async function POST(req: Request) { ... }
```

These are *capabilities*, captured by the capability enumerator. From the surface side, calls to `/api/users` are the consumption.

### Server actions

```ts
// app/actions.ts
'use server'
export async function createUser(formData: FormData) { ... }
```

```tsx
// components/CreateUserForm.tsx
import { createUser } from '@/app/actions'
<form action={createUser}>
```

**Two surface signals:**
1. Import: `kind: hook-import, identifier: createUser` (treat server action import as the same kind as hook import for diff purposes).
2. Form action: `kind: server-action, identifier: createUser` at the `<form action={createUser}>` line.

Both diff against the `server_action` capability. The capability enumerator captures every exported async function in a file with `'use server'` at the top, or any function with `'use server'` as its first body statement.

### Route loaders / actions (Remix-style)

```ts
export async function loader({ params }) {
  return fetch(`/api/users/${params.id}`)
}
```

The loader/action is part of the route surface, but the consumption is the inner fetch. Capture the fetch.

### `use()` hook for data (React 19+)

```tsx
function UserProfile({ userPromise }) {
  const user = use(userPromise)
}
```

Trace upward to the source of `userPromise` — usually a server component fetching directly. Capture the source fetch.

### Server components

Server components run on the server but logically belong to the UI surface from the audit's perspective. A server component with `await db.users.findUnique(...)` is *not* a wiring drift candidate (it's direct data access, not surface-to-capability). Skip database calls in server components — they're implementation, not consumption.

A server component that calls a backend route via `fetch('https://...')` IS a consumption. Capture it.

## React Router

Routing is a UI surface. `<Route path="/users/:id" element={<UserPage />} />` is captured in the surfaces registry but doesn't itself consume anything — only its rendered components do.

Loader/action functions (data router):

```tsx
const router = createBrowserRouter([
  {
    path: "/users/:id",
    loader: async ({ params }) => fetch(`/api/users/${params.id}`),
    element: <UserPage />,
  },
])
```

The loader's `fetch` is a consumption. Capture it as if it were inside the component.

## Form patterns

Form submissions are consumptions:

```tsx
<form
  onSubmit={async (e) => {
    e.preventDefault()
    await fetch('/api/contact', { method: 'POST', body: ... })
  }}
>
```

Capture as `POST /api/contact`.

`<form action="/api/contact" method="post">` (without JS handler) — same identifier, capture from the `action` and `method` attributes.

## Mediated persistence patterns

The audit's central premise — every UI consumption maps to exactly one backend production — fails when an input's value reaches the backend through a *different trigger* than the input itself. These are not bugs; they're legitimate architectural patterns. The audit *will* over-flag them if it doesn't compensate.

When sub-agents see one of these patterns, they should annotate the consumption with `mediated: true` and name the indirect persistence path. The orchestrator's drift-detection step then runs an indirect-persistence probe (see `drift-detection.md` § Mediated persistence calibration) before classifying any setter or input handler as orphan.

### Cycle-coupled batch persistence

User edits accumulate in component state or form state. Persistence happens on a *separate trigger* — "regenerate," "save all," "submit," route navigation, periodic flush — that reads the entire payload at once.

```tsx
function PromptEditor({ initialPrompt, initialCorrections }) {
  const [prompt, setPrompt] = useState(initialPrompt)
  const [corrections, setCorrections] = useState(initialCorrections)
  // setCorrections looks orphan — no direct backend call.
  // But:
  const regenerate = trpc.image.regenerate.useMutation()
  const onRegenerate = () => regenerate.mutate({ prompt, corrections })
  //                                              ^^^^^^^^^^^^ corrections persisted here
}
```

Indicators: a `useMutation` / `useQuery` whose body or `mutationFn` references the orphan'd value, *triggered by a different handler than the setter*. Common in AI/LLM apps with regenerate cycles, multi-step forms with batch save, and editor UIs with explicit save actions.

### Form library state (react-hook-form, Formik)

Form libraries manage state via `register` / `Controller` / `field.onChange` rather than explicit setters. Persistence happens via `handleSubmit` reading the entire form payload.

```tsx
function ProjectSettingsForm({ defaultValues }) {
  const { register, handleSubmit } = useForm({ defaultValues })
  const onSubmit = (data) => trpc.project.update.mutate(data)
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      <input {...register('description')} />
    </form>
  )
}
```

There are *no setters* for `name` or `description` from the audit's perspective — the form library owns the wire. Indicators: imports from `react-hook-form`, `formik`, `react-final-form`, `@tanstack/react-form`. The `register` / `Controller` calls are the indirect-persistence signal.

### URL-as-state

Input value lives in URL query params or route state. "Setting" is `router.replace` / `setSearchParams`, not a state setter.

```tsx
function FilterBar() {
  const [params, setParams] = useSearchParams()
  const status = params.get('status')
  return <Select value={status} onChange={(v) => setParams({ status: v })} />
  //                                       ^^^^^^^^^ "setter" is a URL update
}
```

Backend reads via the URL on its own. Indicators: `useSearchParams`, `useRouter().replace`, `setSearchParams`. The state lives in the URL bar, not in component state.

### Form hydration with batched persistence

Initial values are loaded from the backend on mount (`useQuery`); user edits are tracked in form state; persistence happens via a separate `useMutation` triggered on save/regenerate/navigation.

```tsx
function UserSettings() {
  const { data: user } = trpc.user.me.useQuery()
  const update = trpc.user.update.useMutation()
  const { register, handleSubmit } = useForm({ values: user })  // hydration
  return <form onSubmit={handleSubmit(update.mutate)}>...</form>
}
```

This is the canonical form-with-server-state pattern. The hydration (read) and the persistence (write) flow through *different* identifiers — `user.me` (query) vs `user.update` (mutation). Neither is orphan, but the audit might miss the connection between them.

### Optimistic UI with server reconciliation

Local state mirrors server state and updates locally first, then reconciles via mutation. The local setter is real; the mutation is the persistence path.

```tsx
const [local, setLocal] = useState(serverData)
const update = useMutation({
  mutationFn: (next) => fetch(...),
  onMutate: (next) => setLocal(next),     // optimistic
  onSuccess: () => queryClient.invalidate(['serverData']),  // reconcile
})
```

Indicators: `onMutate` / `onSettled` callbacks that touch local state. The setter is exercised; the mutation is what ultimately reaches the backend.

### Computed/derived inputs

The input's value is derived from another piece of state via a selector or memo. Never written directly.

```tsx
const total = useMemo(() => items.reduce((sum, i) => sum + i.price, 0), [items])
return <input value={total} readOnly />
```

There's no setter at all because the value isn't user-mutable in this layer. Indicators: `useMemo`, `useDerivedValue`, `useSelector` with a computed selector. The audit should not look for a setter for these values.

### Server actions consuming form state

```tsx
'use server'
async function saveAll(formData: FormData) { ... }

// component
<form action={saveAll}>
  <input name="title" defaultValue={post.title} />
  <input name="body" defaultValue={post.body} />
</form>
```

`title` and `body` have no setters — they're submitted as form data on submit. The `action={saveAll}` is the indirect persistence path. Indicators: `<form action={X}>` where `X` is a server action.

## Indirect-persistence probe (sub-agent guidance)

When the surface enumerator sees a useState setter, an `onChange` handler, or any input-tied event handler, before annotating the consumption, scan the same component (and one parent up) for:

1. **Form library imports** — `useForm`, `Formik`, `Controller`, `useFormContext`, `Form.Item`. Annotate as `mediated: form-library`.
2. **Cycle handlers** — `onSubmit`, `onRegenerate`, `onSave`, `handleSubmit`, save-on-navigation handlers. Annotate as `mediated: cycle-coupled`.
3. **URL-state hooks** — `useSearchParams`, `useRouter().replace`, `setSearchParams`. Annotate as `mediated: url-state`.
4. **Mutations referencing the value** — `useMutation` / `useQuery` whose body references the orphan'd value, triggered separately from the setter. Annotate as `mediated: batched-mutation`.
5. **Computed-value indicators** — `useMemo`, `useSelector(selector)`, `useDerivedValue`. Annotate as `mediated: derived`.

Annotation flows through to the orphan-detection step. Annotated consumptions are *not* orphan candidates — they map to the backend via the indirect path, which the orchestrator can name in the report.

## Permission-aware rendering

```tsx
{user.role === 'admin' && <Button onClick={deleteUser}>Delete</Button>}

<Button disabled={!can.editProject(project)} onClick={...}>Edit</Button>
```

Capture the gating expression as `permission_signal` on the wrapped consumption. The audit will diff against the backend handler's auth requirement.

Common patterns:

- Role-based: `user.role === 'admin'`, `'admin' in user.permissions`.
- CASL / abilities: `can('delete', 'Project')`.
- Custom hooks: `useCanDelete()`, `useIsAdmin()`.

When the gate is a custom hook, follow it to its return logic when feasible. When the logic is opaque, capture the hook name as the signal.

## Anti-patterns to flag

These often *correlate with* drift and warrant elevated finding confidence:

### Stringly-typed URL fragments

```ts
const url = `/api/${resource}/${id}`
```

Where `resource` is a parameter. Capture as `kind: http, identifier: dynamic` and mark `confidence: low`. Surface enumerator should still try to enumerate the call sites that reach this code with concrete `resource` values.

### Catch-all dispatch

```ts
api[method](path, ...)   // server-side
client[method](url, ...)  // client-side
```

Defeats static enumeration. The audit notes this and reduces precision in that area.

### Comments naming drift

```tsx
// TODO: this endpoint was renamed, update later
const data = await fetch('/api/old-endpoint')

// FIXME: shape changed in v2, fix the consumer
```

These TODO/FIXME comments are *high-signal* drift markers. The surface enumerator should capture them and the orchestrator should elevate the associated finding's severity.

### Type assertions hiding drift

```ts
const data = await res.json() as User
```

Defeats type-checking. The audit's shape-drift detection can't rely on TypeScript here. When seen, mark the consumption's `response_shape_source: usage-pattern` (inferred from how `data` is used) rather than declared.

## Generic-ness check

For non-React UIs (Vue, Svelte, plain JS, Angular), apply the same pattern but with framework-specific signals:

- Vue: `<script setup>` + `useFetch` (Nuxt), `axios` calls, `<form @submit>`.
- Svelte: `+page.ts` `load()`, `fetch`.
- Angular: services with `HttpClient`, route guards.

The output contract (consumption registry) is unchanged. The signal catalog adapts.

When the audit runs on a non-React UI, surface enumerator's prompt should include the framework's signal patterns inline (the orchestrator constructs the prompt). For React, this file's contents flow into the prompt verbatim.
