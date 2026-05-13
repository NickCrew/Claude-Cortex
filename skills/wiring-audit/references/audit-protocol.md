# Audit Protocol

The orchestrator's playbook. Defines the sub-agent dispatch contract, registry shapes, and the diff sequence. Read this first; the per-side enumeration files (`surface-enumeration.md`, `capability-enumeration.md`) describe *what* each enumerator looks for, but this file describes *how* the audit runs end-to-end.

## Phases

1. **Scope** — establish target, stack, output root, priors.
2. **Dispatch** — two parallel one-shot sub-agents.
3. **Diff** — compute consumption/production set differences.
4. **Categorize** — assign each finding to one of the 8 categories.
5. **Severity** — apply the rubric from `finding-categories.md`.
6. **Verify** — orchestrator-side citation resolution.
7. **Render** — write `report.md`, persist registries, optionally render wiring graph.

## Sub-agent dispatch contract

Two parallel calls in a single message. Both use `general-purpose` with `model: sonnet`. Do not use `team_name` (memory: team-spawned agents lose tools).

### Surface enumerator

Returns YAML:

```yaml
surfaces:
  - id: S-1
    label: <short human label, e.g., "User profile page" or "useCreateProject hook">
    location: <repo-relative-path>:<line>
    kind: component | hook | page | route | form | settings-panel
    consumes:
      - kind: http | trpc | graphql | server-action | hook-import | websocket | env-var | config-key
        identifier: <stable identifier — see below>
        method: <only for kind=http>
        location: <where the consumption happens>:<line>
        evidence: <verbatim line content>
        response_shape: <inferred or declared shape, when available>
        response_shape_source: type-inference | tRPC-procedure-type | OpenAPI | usage-pattern | unknown
        permission_signal: <required role/scope if visible at the call site>
    user_label: <visible UI text when this surface is a button or labelled element>
```

### Capability enumerator

Returns YAML:

```yaml
capabilities:
  - id: C-1
    kind: http_route | trpc_procedure | graphql_field | server_action | exported_hook | websocket_handler | env_var_consumer | config_key_consumer
    identifier: <see below>
    method: <only for kind=http_route>
    location: <repo-relative-path>:<line>
    evidence: <verbatim line content>
    response_shape: <declared or returned shape>
    response_shape_source: declared-type | tRPC-output | GraphQL-schema | inferred-from-return | unknown
    auth: <required guard, e.g., "isAdmin", "session.user.id === params.id", or "none">
    consumed_env: <list of env vars or config keys this capability gates on>
```

### Identifier conventions (stable matching keys)

The diff algorithm matches on `(kind, identifier)`. Identifier formats:

| Kind | Identifier format |
|---|---|
| http / http_route | `<METHOD> <path-template>` e.g., `GET /api/users/:id` |
| trpc / trpc_procedure | dotted path e.g., `users.create` |
| graphql / graphql_field | `<Type>.<field>` e.g., `Query.userById` |
| server-action / server_action | exported function symbol e.g., `createUser` |
| hook-import / exported_hook | hook export symbol e.g., `useUsers` |
| websocket / websocket_handler | event name or topic e.g., `ws:project:update` |
| env-var / env_var_consumer | env var name e.g., `STRIPE_API_KEY` |
| config-key / config_key_consumer | dotted config key e.g., `auth.providers.github.enabled` |

Both enumerators must use the same identifier format. If a sub-agent returns malformed identifiers, re-dispatch *that side only* with the format reinforced.

## The diff (orchestrator's algorithm)

```
consumption_map = {}   # (kind, identifier) -> [consumption_records]
production_map  = {}   # (kind, identifier) -> [production_record]

for surface in surfaces:
    for c in surface.consumes:
        key = (c.kind, c.identifier)
        consumption_map.setdefault(key, []).append({
            "surface_id": surface.id,
            "location": c.location,
            "evidence": c.evidence,
            "method": c.get("method"),
            "shape": c.get("response_shape"),
            "permission": c.get("permission_signal"),
        })

for cap in capabilities:
    key = (cap.kind, cap.identifier)
    production_map.setdefault(key, []).append({
        "capability_id": cap.id,
        "location": cap.location,
        "evidence": cap.evidence,
        "method": cap.get("method"),
        "shape": cap.get("response_shape"),
        "auth": cap.get("auth"),
    })

findings = []

# Orphan surfaces: consumed but not produced.
for key in consumption_map:
    if key not in production_map:
        for c in consumption_map[key]:
            # Mediated-persistence calibration — see drift-detection.md.
            # If consumption was annotated `mediated: ...` by the surface
            # enumerator, OR the indirect-persistence probe finds a form
            # library / cycle handler / URL-state / batched mutation in
            # the same component, downgrade severity from broken to
            # mediated and tag the finding's notes with the indirect path.
            mediated = c.get("mediated") or run_indirect_persistence_probe(c)
            findings.append(orphan_surface_finding(key, c, mediated=mediated))

# Unwired capabilities: produced but not consumed.
for key in production_map:
    if key not in consumption_map:
        for p in production_map[key]:
            findings.append(unwired_capability_finding(key, p))

# Drift: in both — compare shape, method, auth.
for key in consumption_map:
    if key in production_map:
        for c in consumption_map[key]:
            for p in production_map[key]:
                findings.extend(compare_shapes(c, p))
                findings.extend(compare_methods(c, p))    # http only
                findings.extend(compare_auth(c, p))        # if both have permission/auth signals
```

The 1:N case is real (one consumer of a capability that several surfaces share). Multiple surfaces consuming the same capability is fine; pair each consumer with the producer for shape/method comparison.

## Stale label detection (separate pass)

Stale labels don't fit the diff cleanly because they're text-on-the-wire, not code-on-the-wire. Run after the main diff:

1. From the surfaces registry, collect every `user_label` that contains a noun phrase (heuristic: 1–4 words, no whitespace-stripped lowercase, often capitalized).
2. For each label, search the capability registry for a capability whose identifier or evidence references the noun phrase.
3. If the label's noun phrase appears in NO capability evidence, but a *similar* phrase does (one rename hop — Levenshtein distance ≤ 3, or a known pattern like `commit_pending` ↔ "Save Draft"), flag a stale-label finding.

This is heuristic — false positives are normal. Severity is `stale` by default; the report's narrative explains the inferred rename.

## Verification

For each candidate finding before it lands in the report:

1. **UI side citation** — `Read` the cited line, confirm content matches `evidence`.
2. **Backend side citation** — same.
3. **Absence claim** — for orphan-surface findings, grep the asserted-missing identifier across the *backend subtree*. If it turns up, discard the finding (the enumerator missed it).
4. **Severity sanity** — broken-severity findings must have both citations resolved (not just one). Discard if the backend side is unresolvable for an orphan claim *unless* the grep evidence is documented.

Maintain a discard log for the verification section of `report.md`.

## Re-dispatch

If a sub-agent returns malformed output (missing identifiers, prose-only, wrong YAML shape), re-dispatch *that side only* with the format requirement sharpened. Limit to two re-dispatches per side; on the third failure, escalate to the user (the codebase may have non-standard surface or capability patterns the audit doesn't recognize).

## Composing with architectural-analysis

If `docs/architecture/<recent-date>/` exists:

- The UI-surfaces report's callouts feed the surface enumerator's prompt as priors. The enumerator's job becomes "find what each surface *consumes*" rather than "find every surface" — saving substantial work.
- The integrations report's callouts feed the capability enumerator's prompt similarly.

Pass the priors as a `priors:` block in the prompt:

```
priors:
  ui_surfaces:
    - id: U-7
      label: Settings page
      location: src/pages/Settings.tsx:1
    - id: U-12
      label: useUserMutation
      location: src/hooks/users.ts:14
```

The sub-agent uses these as the surface set and focuses on enumerating consumptions. Same shape applies for capabilities ↔ integrations.
