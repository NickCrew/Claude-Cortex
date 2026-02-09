# Perspective Catalog

Maps review perspectives to trigger signals and relevant skills. Use this catalog to
determine which perspectives apply to a given diff and which skills to load for each.

## Perspectives

### Correctness

**Trigger signals**: Any code change — logic, control flow, data transformation, state mutation.

**Focus**: Logic errors, off-by-one, null/undefined handling, edge cases, race conditions,
contract violations, type mismatches, incomplete error propagation.

**Relevant skills**: (none required — this is a foundational perspective that applies universally)

---

### Security

**Trigger signals**: Auth/authz code, user input handling, API endpoints, database queries,
file operations, secrets/env vars, crypto, HTTP headers, CORS, cookie handling, dependencies.

**Relevant skills**:
- `owasp-top-10` — OWASP Top 10 vulnerability detection and remediation
- `secure-coding-practices` — Defensive programming, input validation, output encoding
- `threat-modeling-techniques` — STRIDE analysis, attack surface evaluation
- `security-testing-patterns` — SAST/DAST patterns, vulnerability assessment

---

### Performance

**Trigger signals**: Loops over collections, database queries, network calls, file I/O,
memory allocation, caching logic, batch operations, algorithmic changes, rendering paths.

**Relevant skills**:
- `python-performance-optimization` — Profiling, vectorization, memory optimization (Python files)
- `react-performance-optimization` — Memoization, code splitting, render optimization (React files)
- `workflow-performance` — Systematic performance analysis methodology
- `database-design-patterns` — Query optimization, indexing (when DB queries involved)

---

### Maintainability

**Trigger signals**: Any code change — naming, structure, coupling, cohesion, duplication,
complexity, readability, abstraction levels.

**Focus**: Naming clarity, single responsibility, DRY violations, cognitive complexity,
dead code introduction, unclear intent, missing context, over-abstraction, under-abstraction.

**Relevant skills**:
- `code-quality-workflow` — Quality assessment methodology and improvement patterns

---

### Testing

**Trigger signals**: Test file changes, testable logic additions, public API changes,
bug fixes (regression test needed), new error paths.

**Focus**: Test coverage gaps, assertion quality, edge case coverage, test isolation,
mock appropriateness, flaky test introduction, missing negative tests.

**Relevant skills**:
- `python-testing-patterns` — pytest patterns, mocking, property-based testing (Python)
- `test-generation` — Coverage-driven test creation methodology
- `test-driven-development` — TDD red-green-refactor discipline
- `testing-anti-patterns` — Test smells, bad mocking, test-only production code

---

### Architecture

**Trigger signals**: New modules/packages, cross-boundary imports, interface changes,
dependency additions, service communication, data flow changes, configuration structure.

**Focus**: Layer violations, coupling direction, dependency inversion, interface segregation,
domain boundary integrity, circular dependencies, abstraction leaks.

**Relevant skills**:
- `system-design` — Component design, data modeling, interface contracts
- `api-design-patterns` — REST/GraphQL patterns, versioning, error contracts
- `microservices-patterns` — Service decomposition, communication patterns (if distributed)
- `event-driven-architecture` — Event sourcing, CQRS (if event-based patterns present)

---

### Infrastructure

**Trigger signals**: Terraform/HCL files, Kubernetes manifests, Helm charts, Dockerfiles,
CI/CD configs, deployment scripts, cloud resource definitions.

**Focus**: Resource misconfiguration, missing limits/quotas, insecure defaults,
state management, drift potential, blast radius.

**Relevant skills**:
- `terraform-best-practices` — IaC patterns, state management, module design
- `kubernetes-deployment-patterns` — Deployment strategies, workload patterns
- `kubernetes-security-policies` — RBAC, pod security, network policies
- `helm-chart-patterns` — Chart templates, values management
- `gitops-workflows` — ArgoCD/Flux declarative deployment

---

### API Contract

**Trigger signals**: Endpoint additions/modifications, request/response schema changes,
status code changes, header modifications, serialization changes, versioning.

**Focus**: Breaking changes, backwards compatibility, error response consistency,
pagination patterns, authentication/authorization headers, rate limiting.

**Relevant skills**:
- `api-design-patterns` — REST/GraphQL design, versioning, HATEOAS
- `api-gateway-patterns` — Routing, rate limiting, BFF patterns

---

### Accessibility

**Trigger signals**: HTML/JSX/TSX changes, CSS changes, component props for aria-*,
role attributes, focus management, color values, form elements, image tags.

**Focus**: WCAG 2.2 AA compliance, keyboard navigation, screen reader compatibility,
color contrast, semantic HTML, focus management, form labeling.

**Relevant skills**:
- `accessibility-audit` — WCAG 2.2 AA triage for pages and components

---

### UX / Design

**Trigger signals**: UI component changes, layout modifications, user flow changes,
error message text, loading states, empty states, form interactions.

**Focus**: User flow coherence, error messaging clarity, loading/empty states,
progressive disclosure, interaction feedback, visual consistency.

**Relevant skills**:
- `ux-review` — Multi-perspective UX review (usability, accessibility, interaction)
- `ui-design-aesthetics` — Visual quality, progressive disclosure, design patterns

## Perspective Selection Rules

1. **Always include**: Correctness, Maintainability (these apply to every code change)
2. **Include by file type**:
   - `.py` files → consider Performance (Python), Testing (Python)
   - `.tsx`/`.jsx`/`.html`/`.css` files → consider Accessibility, UX/Design, Performance (React)
   - `.tf`/`.hcl` files → Infrastructure
   - `Dockerfile`, `*.yaml` (k8s) → Infrastructure
   - `*test*`/`*spec*` files → Testing
3. **Include by content signals**: Scan diff hunks for trigger signals listed above
4. **Limit scope**: Select 3-5 perspectives maximum to maintain review depth and quality
5. **Prioritize**: If more than 5 perspectives seem relevant, select the 5 most impactful
   based on the volume and nature of changes
