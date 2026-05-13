# Drift Detection

The diff algorithm. Run by the orchestrator after both enumerators return. This is the core of the audit — every finding category falls out of the same set-comparison logic.

## Step 1 — Build the maps

```python
consumption_map: dict[tuple[Kind, Identifier], list[Consumption]] = defaultdict(list)
production_map:  dict[tuple[Kind, Identifier], list[Production]]  = defaultdict(list)

for surface in registry.surfaces:
    for c in surface.consumes:
        consumption_map[(c.kind, c.identifier)].append(
            Consumption(
                surface_id=surface.id,
                location=c.location,
                evidence=c.evidence,
                method=c.get("method"),
                shape=c.get("response_shape"),
                permission=c.get("permission_signal"),
            )
        )

for cap in registry.capabilities:
    production_map[(cap.kind, cap.identifier)].append(
        Production(
            capability_id=cap.id,
            location=cap.location,
            evidence=cap.evidence,
            method=cap.get("method"),
            shape=cap.get("response_shape"),
            auth=cap.get("auth"),
        )
    )
```

## Step 2 — Identifier normalization

Before diffing, normalize identifiers to maximize matches:

- **HTTP paths**: lowercase the path; collapse trailing slashes; templatize numeric/UUID concrete IDs in URLs to `:param` (matching the surface enumerator's templating).
- **Methods**: uppercase HTTP verbs.
- **tRPC paths**: trim whitespace; case-sensitive (tRPC procedure names are case-sensitive).
- **GraphQL fields**: case-sensitive `<Type>.<field>` exactly.
- **Hook symbols**: case-sensitive function name.
- **Env vars**: uppercase, exact match.
- **Config keys**: case-sensitive, dot-separated.

Two consumptions or productions whose identifiers differ only by normalization are treated as the same key — no method-drift finding for `GET` vs `get`.

## Step 3 — Set differences

```python
findings = []

# Orphan surfaces — consumed, not produced.
for key, consumptions in consumption_map.items():
    if key not in production_map:
        for c in consumptions:
            findings.append(orphan_surface(key, c))

# Unwired capabilities — produced, not consumed.
for key, productions in production_map.items():
    if key not in consumption_map:
        for p in productions:
            findings.append(unwired_capability(key, p))
```

### Near-match detection (orphans)

Before recording an orphan, check for *near-matches* in the other map:

- **Levenshtein distance ≤ 2** on the identifier string → likely typo or rename.
- **Same identifier, different method** (HTTP only) → method-drift candidate, not orphan.
- **Same path, different parameter shape** (`:id` vs `:userId`) → likely rename, surface as drift with high-confidence note.

If a near-match exists, the finding is upgraded from orphan-surface to **method-drift** or **stale-rename** (a flavor of drift) with both citations.

### Mediated persistence calibration (orphans)

The audit's central premise — every consumption maps to exactly one production — fails for **mediated persistence**: patterns where a UI input's value reaches the backend through a *different trigger* than the input itself. Common shapes:

- **Cycle-coupled batch persistence** — user edits accumulate in form state; persistence happens on a "regenerate," "save all," or "submit" action that reads the entire form payload.
- **Form library state** — `react-hook-form`, `Formik`, controlled inputs via libraries that use `register` / `Controller` / `field.onChange`, not direct state setters.
- **URL-as-state** — input value lives in `useSearchParams` or route params; "setting" is a `router.replace(...)` call, not a state setter.
- **Optimistic-with-batched-write** — UI reads from `useQuery`, accumulates local edits, persists via a single `useMutation` on a separate trigger.
- **Computed/derived inputs** — the input's value is derived from another piece of state via a selector or memo; never written directly.

In all of these, a setter or `onChange` handler can *look orphan* (no direct backend call from the setter) while the input genuinely works. The audit will over-flag if it doesn't compensate.

Before recording an orphan-surface finding for a setter, input handler, or hook that lives in a UI component, the orchestrator runs an **indirect-persistence probe** in the same component (or its parent up to two levels):

1. Look for a form library import (`useForm`, `Formik`, `Form.Item`, `Controller`, `register`, `useFormContext`). If present, the input is mediated — downgrade from `broken` to `mediated` and tag the finding's `notes` with the form library name.
2. Look for a `useSearchParams`, `useRouter().replace`, or URL-state library import in the same component. If present and the input value flows into a URL update, mark mediated.
3. Look for a sibling event handler (commonly named `onSubmit`, `onRegenerate`, `onSave`, `handleSubmit`) that reads from form state or component-level state including the orphan'd input. If present, the input is cycle-coupled — mark mediated.
4. Look for a `useMutation` / `useQuery` whose body or `mutationFn` references the orphan'd value. If present, mark mediated.

When the probe matches any of (1)–(4), the finding becomes severity `mediated` (a non-broken severity meaning "indirect path exists, manual review needed"). The report's narrative should explicitly call out which probe triggered.

The probe is intentionally conservative: false negatives (missed mediation, finding stays orphan) are recoverable by user reading; false positives (mediated tag on a genuinely orphan setter) just delay action by one verification cycle. Over-reporting orphans is the worse failure mode — it erodes trust in the audit fast.

If the probe finds *no* indirect path, the orphan finding stands at its default `broken` severity.

## Step 4 — Shape comparison (matched pairs)

For each `key` in *both* maps, compare:

```python
for key in consumption_map:
    if key in production_map:
        for c in consumption_map[key]:
            for p in production_map[key]:
                # method drift (HTTP only)
                if c.method and p.method and c.method != p.method:
                    findings.append(method_drift(c, p))

                # shape drift
                if c.shape and p.shape:
                    diff = shape_diff(c.shape, p.shape)
                    if diff:
                        findings.append(shape_drift(c, p, diff))

                # auth/permission drift
                if c.permission or p.auth:
                    if not auth_aligned(c.permission, p.auth):
                        findings.append(permission_drift(c, p))
```

### Shape diff

For object shapes, check field-by-field:

- **Field on consumption side, missing on production side**: `consumption expects field X, production never returns it`.
- **Field on production side, ignored on consumption side**: usually not a finding (frontend doesn't have to use everything backend returns), unless the field is required and the consumption code path crashes when absent.
- **Field on both, types differ**: `expected string, got number` etc. — high-confidence drift finding.
- **Field renamed**: heuristic — if a field on one side has a similarly-named field on the other (`first_name` ↔ `firstName`, `userId` ↔ `user_id`), flag as case-style drift with severity `drifted`.

When shapes are inferred (no explicit type), confidence drops. The finding's `confidence` field reflects this.

## Step 5 — Validation drift (optional pass)

Run when zod / yup / joi schemas are detected on both sides:

```ts
// frontend
const FormSchema = z.object({ email: z.string().email().max(320), age: z.number().min(0) })

// backend handler
const ApiSchema = z.object({ email: z.string().email().max(100), age: z.number().min(13).max(120) })
```

Diff the schemas:

- Different `.max()` / `.min()`: validation-drift finding.
- Different `.email()`, `.url()`, `.regex()` constraints: validation-drift.
- Required vs optional mismatch: validation-drift.

When schemas are imported from a shared module, no drift is possible — note that the project has a shared validation module and skip this pass for fields covered by it.

## Step 6 — Permission drift

```python
def auth_aligned(consumption_perm, production_auth):
    if consumption_perm is None and production_auth in ("none", None):
        return True   # both unguarded
    if consumption_perm and production_auth in ("none", None):
        return False  # UI gates, backend doesn't (often a real bug)
    if consumption_perm is None and production_auth and production_auth != "none":
        return False  # backend gates, UI doesn't (often shows-then-fails)
    # both gate — heuristic match on the gating expression
    return permission_expressions_match(consumption_perm, production_auth)
```

The `permission_expressions_match` heuristic:

- Both contain the word `admin` → aligned.
- Both reference `session.user.id === <param>` → aligned (both gate on self).
- Mismatched roles or scopes → permission-drift finding.

False positives are common here. Severity stays at `drifted` unless the production side has `auth: none` while the consumption side gates — that case is upgradable to `broken` because the backend genuinely lacks enforcement.

## Step 7 — Stale label detection

Run after the main diff:

```python
all_labels = collect_user_labels(registry.surfaces)
all_capability_evidence = collect_evidence_strings(registry.capabilities)

for label, label_location in all_labels:
    noun_phrases = extract_noun_phrases(label)
    for phrase in noun_phrases:
        # Phrase in current capability evidence?
        if any(phrase.lower() in e.lower() for e in all_capability_evidence):
            continue   # current; not stale.
        # Find candidate renames — phrases differing by ≤ 3 edit distance.
        candidates = find_near_matches(phrase, all_capability_evidence, threshold=3)
        if candidates:
            findings.append(stale_label(
                label=label,
                label_location=label_location,
                phrase=phrase,
                near_matches=candidates,
            ))
```

This is heuristic — both false positives and false negatives are expected. Default severity `stale`. Note the finding's `confidence` field as `low` since the heuristic can't distinguish a renamed concept from a coincidentally-similar word.

## Step 8 — Unsurfaced configuration

For each `env_var_consumer` and `config_key_consumer` capability:

- Check if any surface's `consumes[]` references the same env var or config key.
- Check if there's an admin UI / settings page / CLI flag that lets a user set the value (heuristic: search the surface registry for buttons or inputs whose label or attribute name contains the var/key).
- Check if there's a `.env.example` or `config.example.toml` that documents the var/key.

If the var/key is consumed in code but has neither a settings surface nor documentation, flag as **unsurfaced-config** with severity `gap`.

## Step 9 — Output

The orchestrator passes the findings list through severity sorting (`finding-categories.md` rubric) and citation verification (`audit-protocol.md` step 6) before rendering to `report.md`.

## Notes on false positives

Each diff step can produce false positives. Calibration:

- **Wrapper functions**: a custom HTTP wrapper might obscure URLs — if the surface enumerator can't templatize the wrapper's parameters, mark consumption with `confidence: low` and the orchestrator de-prioritizes it.
- **Dynamic dispatch**: `app[method](path, handler)` style routing in Express defeats static enumeration. Sub-agent should note when it sees dynamic dispatch and capabilities are flagged with `dynamic_dispatch: true`. Diff treats them as wildcard matches.
- **Code-generated routers**: tRPC's generated `useQuery` is heavily reliant on type inference; generated clients can lose precision. Note in finding's confidence.
- **Test routes**: `pages/api/test/...` or routes guarded by `if (env === 'test')` should be marked `dev-only: true` and excluded from the diff by default.

## Tooling preference

- **codanna** when `.codanna/` exists — fast symbol resolution.
- **`Read`** for line-content verification.
- **`grep`** for absence checks across subtrees.
- **TypeScript compiler API** is overkill for the audit; sub-agents can read types out of source files directly via `Read`.
