# Mermaid Diagram Types Reference

Syntax, patterns, and code examples for every major Mermaid diagram type.

---

## Flowchart

Best for: process flows, decision trees, system overviews.

### Basic Syntax

```mermaid
flowchart TD
    A["Start"] --> B{"Decision?"}
    B -->|Yes| C["Action 1"]
    B -->|No| D["Action 2"]
    C --> E["End"]
    D --> E
```

### Direction Options

| Direction | Meaning |
|-----------|---------|
| `TD` / `TB` | Top to bottom |
| `BT` | Bottom to top |
| `LR` | Left to right |
| `RL` | Right to left |

### Node Shapes

```mermaid
flowchart LR
    A["Rectangle — default"]
    B("Rounded rectangle")
    C(["Stadium / pill"])
    D[["Subroutine"]]
    E[("Database / cylinder")]
    F{"Diamond — decision"}
    G{{"Hexagon"}}
    H>"Asymmetric / flag"]
    I(("Circle"))
    J{{" Double circle"}}
```

### Edge Types

```mermaid
flowchart LR
    A --> B
    A --- C
    A -.-> D
    A ==> E
    A --"label"--> F
    A -.."dashed label".-> G
    A =="thick label"==> H
```

| Syntax | Meaning |
|--------|---------|
| `-->` | Solid arrow |
| `---` | Solid line (no arrow) |
| `-.->` | Dashed arrow |
| `==>` | Thick arrow |
| `--"text"-->` | Labeled arrow |
| `~~~` | Invisible link (for layout) |

### Subgraphs

```mermaid
flowchart TB
    subgraph Frontend
        A["React App"] --> B["API Client"]
    end
    subgraph Backend
        C["API Server"] --> D["Database"]
    end
    B --> C
```

### Styling

```mermaid
flowchart LR
    A["Normal"]:::default
    B["Success"]:::success
    C["Error"]:::error

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef success fill:#d4edda,stroke:#28a745,stroke-width:2px
    classDef error fill:#f8d7da,stroke:#dc3545,stroke-width:2px
```

---

## Sequence Diagram

Best for: API interactions, message passing, time-ordered communication.

### Basic Syntax

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: POST /api/login
    activate S
    S->>DB: SELECT user WHERE email = ?
    DB-->>S: User record
    S-->>C: 200 OK + JWT token
    deactivate S
```

### Arrow Types

| Syntax | Meaning |
|--------|---------|
| `->>` | Solid arrow (synchronous) |
| `-->>` | Dashed arrow (response/async) |
| `-x` | Solid arrow with X (lost message) |
| `--x` | Dashed arrow with X |
| `-)` | Solid arrow, open end (async fire-and-forget) |
| `--)` | Dashed arrow, open end |

### Features

**Activation boxes:**
```mermaid
sequenceDiagram
    A->>B: Request
    activate B
    B->>C: Sub-request
    activate C
    C-->>B: Response
    deactivate C
    B-->>A: Response
    deactivate B
```

**Loops and conditions:**
```mermaid
sequenceDiagram
    Client->>Server: Request

    alt valid token
        Server-->>Client: 200 OK
    else expired token
        Server-->>Client: 401 Unauthorized
        Client->>Server: Refresh token
        Server-->>Client: New token
    end

    loop Every 30s
        Client->>Server: Heartbeat
    end

    opt Debug mode
        Server->>Logger: Log request details
    end
```

**Notes:**
```mermaid
sequenceDiagram
    A->>B: Message
    Note over A,B: This spans both participants
    Note right of B: This is a side note
```

---

## Class Diagram

Best for: object models, inheritance, interfaces.

### Basic Syntax

```mermaid
classDiagram
    class User {
        +String name
        +String email
        -String passwordHash
        +login(credentials) bool
        +logout() void
    }

    class Admin {
        +String[] permissions
        +grantRole(user, role) void
    }

    User <|-- Admin : extends
```

### Relationship Types

| Syntax | Meaning |
|--------|---------|
| `<\|--` | Inheritance |
| `*--` | Composition |
| `o--` | Aggregation |
| `-->` | Association |
| `..>` | Dependency |
| `..\|>` | Realization / implements |

### Cardinality

```mermaid
classDiagram
    User "1" --> "*" Order : places
    Order "1" --> "1..*" LineItem : contains
    LineItem "*" --> "1" Product : references
```

---

## State Diagram

Best for: lifecycle states, workflow transitions, finite state machines.

### Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : submit
    Review --> Approved : approve
    Review --> Draft : request_changes
    Approved --> Published : publish
    Published --> Archived : archive
    Archived --> [*]
```

### Composite States

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Processing : receive_request
        Processing --> Idle : complete
        Processing --> Error : failure
        Error --> Idle : retry
    }

    Active --> Shutdown : terminate
    Shutdown --> [*]
```

### Transitions with Guards

```mermaid
stateDiagram-v2
    Pending --> Approved : review [score >= 80]
    Pending --> Rejected : review [score < 80]
```

---

## Entity Relationship Diagram

Best for: database schemas, data models.

### Basic Syntax

```mermaid
erDiagram
    USER {
        int id PK
        string name
        string email UK
        timestamp created_at
    }

    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
        timestamp ordered_at
    }

    LINE_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }

    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }

    USER ||--o{ ORDER : "places"
    ORDER ||--|{ LINE_ITEM : "contains"
    PRODUCT ||--o{ LINE_ITEM : "referenced in"
```

### Relationship Notation

| Left | Right | Meaning |
|------|-------|---------|
| `\|\|` | `\|\|` | Exactly one to exactly one |
| `\|\|` | `o{` | One to zero or more |
| `\|\|` | `\|{` | One to one or more |
| `o\|` | `o{` | Zero or one to zero or more |

---

## Gantt Chart

Best for: project timelines, task scheduling, dependencies.

### Basic Syntax

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    excludes weekends

    section Planning
    Requirements gathering :a1, 2026-01-06, 5d
    Architecture design    :a2, after a1, 3d

    section Development
    Backend implementation :b1, after a2, 10d
    Frontend implementation :b2, after a2, 8d
    Integration            :b3, after b1, 5d

    section Testing
    QA testing             :c1, after b3, 5d
    UAT                    :c2, after c1, 3d

    section Release
    Deployment             :milestone, after c2, 0d
```

### Task Status

```mermaid
gantt
    section Tasks
    Completed task :done, t1, 2026-01-06, 3d
    Active task    :active, t2, after t1, 3d
    Future task    :t3, after t2, 3d
    Critical task  :crit, t4, after t3, 2d
    Milestone      :milestone, after t4, 0d
```

---

## Pie Chart

Best for: proportional data, distribution breakdowns.

```mermaid
pie title Code Coverage by Module
    "Auth" : 92
    "API" : 87
    "Database" : 78
    "UI" : 65
    "Utils" : 95
```

---

## Mindmap

Best for: hierarchical brainstorming, topic organization.

```mermaid
mindmap
  root((System Architecture))
    Frontend
      React SPA
      Mobile App
      Admin Dashboard
    Backend
      API Gateway
      Auth Service
      Business Logic
    Data Layer
      PostgreSQL
      Redis Cache
      S3 Storage
    Infrastructure
      Kubernetes
      CI/CD Pipeline
      Monitoring
```

---

## Timeline

Best for: historical events, version history, milestones.

```mermaid
timeline
    title Product Release History
    2024 : v1.0 Launch
         : v1.1 Bug fixes
    2025 : v2.0 Major rewrite
         : v2.1 Performance improvements
         : v2.2 API expansion
    2026 : v3.0 Cloud-native architecture
```

---

## Git Graph

Best for: branching strategies, release flows.

```mermaid
gitGraph
    commit id: "init"
    branch develop
    commit id: "feat-1"
    commit id: "feat-2"
    branch feature/auth
    commit id: "auth-impl"
    commit id: "auth-tests"
    checkout develop
    merge feature/auth
    checkout main
    merge develop tag: "v1.0.0"
    branch hotfix/security
    commit id: "patch"
    checkout main
    merge hotfix/security tag: "v1.0.1"
```

---

## User Journey

Best for: user experience flows, satisfaction mapping.

```mermaid
journey
    title User Onboarding Experience
    section Sign Up
      Visit landing page: 5: User
      Fill registration form: 3: User
      Verify email: 2: User
    section First Use
      Complete tutorial: 4: User
      Create first project: 4: User
      Invite team member: 3: User
    section Activation
      Use core feature: 5: User
      Set up integration: 3: User
```

The number (1-5) represents user satisfaction at that step.

---

## Styling Tips

### Global Theme Configuration

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#4A90D9',
    'primaryTextColor': '#fff',
    'primaryBorderColor': '#2C6FAC',
    'lineColor': '#666',
    'secondaryColor': '#F5A623',
    'tertiaryColor': '#7ED321',
    'fontSize': '14px'
  }
}}%%
```

### Available Themes

| Theme | Use for |
|-------|---------|
| `default` | Standard Mermaid colors |
| `neutral` | Grayscale, print-friendly |
| `dark` | Dark backgrounds |
| `forest` | Green-toned |
| `base` | Customizable starting point |

### Accessibility Checklist

- [ ] Colors have sufficient contrast (WCAG AA minimum)
- [ ] Meaning is not conveyed by color alone (use labels and shapes)
- [ ] Diagrams have alt text when embedded in HTML/markdown
- [ ] Complex diagrams include a text summary
- [ ] Font size is readable (14px minimum)
