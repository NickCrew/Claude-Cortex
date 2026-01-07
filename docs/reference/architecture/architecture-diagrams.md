# Cortex Architecture Diagrams

Visual documentation of the three-layer automation system.

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        User[👤 User Input]
        Commands["/slash:commands<br/>43 commands<br/>16 namespaces"]
        Flags["--flags<br/>--brainstorm, --ultrathink<br/>--focus, --orchestrate"]
    end

    subgraph "Layer 2: Behavioral Modes"
        Brainstorm[🤝 Brainstorm<br/>Socratic dialogue]
        DeepAnalysis[🔬 Deep Analysis<br/>Max reasoning]
        QualityFocus[✨ Quality Focus<br/>8/10, 90%]
        TokenEfficient[📦 Token Efficient<br/>30-50% reduction]
        ParallelOrch[⚡ Parallel Orchestration<br/>Parallel execution]
        SuperSaiyan[🔥 Super Saiyan<br/>Visual excellence]
        TaskMgmt[📋 Task Management<br/>Hierarchical tasks]
    end

    subgraph "Layer 3: Workflows"
        FeatureDev[🚀 Feature Development<br/>9 steps]
        BugFix[🐛 Bug Fix<br/>8 steps]
        Refactor[♻️ Refactoring<br/>10 steps]
        APIDev[🎯 API Design<br/>15 steps]
        TechDebt[🧹 Tech Debt<br/>13 steps]
        ArchReview[🏗️ Architecture<br/>15 steps]
        Onboard[👋 Onboarding<br/>17 steps]
        Security[🔒 Security Audit<br/>8 steps]
        Perf[⚡ Performance<br/>10 steps]
    end

    subgraph "Layer 4: Execution"
        Agents[🤖 Specialized Agents<br/>code-reviewer, test-automator<br/>security-auditor, etc.]
        MCP[🔌 MCP Servers<br/>Codanna, Context7<br/>Sequential]
        Tools[🛠️ Native Tools<br/>Read, Write, Edit<br/>Bash, Grep, etc.]
    end

    User --> Commands
    User --> Flags
    Commands --> Brainstorm
    Commands --> DeepAnalysis
    Commands --> QualityFocus
    Flags --> TokenEfficient
    Flags --> ParallelOrch

    Brainstorm --> FeatureDev
    Brainstorm --> APIDev
    Brainstorm --> Onboard

    DeepAnalysis --> Refactor
    DeepAnalysis --> TechDebt
    DeepAnalysis --> ArchReview

    QualityFocus --> Refactor
    QualityFocus --> TechDebt

    ParallelOrch --> FeatureDev
    ParallelOrch --> Refactor
    ParallelOrch --> APIDev

    FeatureDev --> Agents
    BugFix --> Agents
    Refactor --> Agents
    APIDev --> Agents

    Agents --> MCP
    Agents --> Tools

    style User fill:#e1f5ff
    style Commands fill:#ffe1e1
    style Brainstorm fill:#fff3e1
    style DeepAnalysis fill:#fff3e1
    style QualityFocus fill:#fff3e1
    style FeatureDev fill:#e8f5e9
    style Agents fill:#f3e5f5
    style MCP fill:#f3e5f5
```

---

## Command → Mode → Workflow Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as /slash:command
    participant M as 🎨 Mode
    participant W as 🔄 Workflow
    participant A as 🤖 Agents
    participant T as 📋 TodoWrite

    U->>C: /refactor:analyze src/auth

    Note over C: Parse command<br/>Load configuration

    C->>M: Activate Deep_Analysis
    C->>M: Activate Quality_Focus

    Note over M: Set behavior:<br/>- Max reasoning depth<br/>- Quality threshold 8/10<br/>- Coverage target 90%

    M->>W: Trigger refactoring workflow

    Note over W: Load workflow steps<br/>Initialize state

    W->>T: Create progress tracking
    T-->>U: Show task list

    W->>A: Execute Step 1: Code Analysis
    A->>A: code-reviewer agent
    A-->>W: quality_report, refactoring_candidates

    W->>T: Update: Step 1 ✅
    T-->>U: Progress: 1/10 (10%)

    W->>A: Execute Step 2: Impact Assessment
    A->>A: Codanna MCP (analyze_impact)
    A-->>W: dependency_graph, risk_assessment

    W->>T: Update: Step 2 ✅
    T-->>U: Progress: 2/10 (20%)

    W->>A: Execute Step 3: Refactoring Plan
    A->>A: Planning with Deep_Analysis
    A-->>W: refactoring_plan, safety_checkpoints

    W->>T: Update: Step 3 ✅

    Note over W: Continue through<br/>remaining steps...

    W-->>U: ✅ Workflow Complete<br/>📄 Refactoring plan generated
```

---

## Mode Activation Flow

```mermaid
flowchart TB
    Start([User Input]) --> Detect{Detect Trigger?}

    Detect -->|Manual| Manual["/mode:activate"]
    Detect -->|Flag| Flag["--brainstorm<br/>--ultrathink<br/>--focus quality"]
    Detect -->|Auto| Auto["Keywords:<br/>'maybe', 'not sure'<br/>'refactor', 'analyze'"]
    Detect -->|Workflow| Workflow["Workflow step<br/>specifies mode"]

    Manual --> LoadMode[Load Mode Configuration]
    Flag --> LoadMode
    Auto --> LoadMode
    Workflow --> LoadMode

    LoadMode --> ParseDef[Parse Mode Definition]
    ParseDef --> SetBehavior[Set Behavioral Changes]

    SetBehavior --> Behavior{Mode Type?}

    Behavior -->|Brainstorm| B1["- Ask clarifying questions<br/>- Present options<br/>- Use AskUserQuestion<br/>- Build shared understanding"]

    Behavior -->|Deep Analysis| B2["- Extended reasoning depth<br/>- Hypothesis generation<br/>- Evidence-based conclusions<br/>- Transparency markers"]

    Behavior -->|Quality Focus| B3["- Review threshold: 8/10<br/>- Coverage target: 90%<br/>- Elevated standards<br/>- Zero tolerance issues"]

    Behavior -->|Token Efficient| B4["- Symbol communication<br/>- 30-50% reduction<br/>- Eliminate redundancy<br/>- Structured compression"]

    Behavior -->|Parallel Orch| B5["- Parallel-first mindset<br/>- Quality gates mandatory<br/>- Agent maximization<br/>- Workstream coordination"]

    B1 --> Active[Mode Active ✅]
    B2 --> Active
    B3 --> Active
    B4 --> Active
    B5 --> Active

    Active --> Execute[Execute Task<br/>with Mode Behavior]

    Execute --> Deactivate{Deactivate?}

    Deactivate -->|Session End| End1([Mode Ends])
    Deactivate -->|Task Complete| End2([Mode Ends])
    Deactivate -->|Manual /mode:deactivate| End3([Mode Ends])
    Deactivate -->|Permanent| Persist[Persist to Profile]

    Persist --> End4([Mode Remains Active])

    style Start fill:#e1f5ff
    style LoadMode fill:#fff3e1
    style Active fill:#c8e6c9
    style Execute fill:#bbdefb
```

---

## Workflow Execution Flow

```mermaid
flowchart TD
    Start(["/workflow:run feature-development"]) --> Load[Load Workflow YAML]

    Load --> Validate{Validate<br/>Definition?}
    Validate -->|Invalid| Error1[❌ Report Error]
    Validate -->|Valid| Init[Initialize Workflow State]

    Init --> CreateTasks[Create TodoWrite Tasks<br/>for Each Step]
    CreateTasks --> SetupOutputs[Setup Output Directory<br/>./workflow-outputs/]

    SetupOutputs --> Step1[Step 1: Architecture Design]

    Step1 --> LoadMode1[Load Required Mode:<br/>Deep_Analysis]
    LoadMode1 --> Agent1[Activate Agent:<br/>system-architect]
    Agent1 --> Execute1[Execute Step 1]
    Execute1 --> Validate1{Outputs<br/>Valid?}

    Validate1 -->|No| Retry1[Retry or Fail]
    Validate1 -->|Yes| Update1[Update TodoWrite: ✅]

    Update1 --> Checkpoint1[Save Checkpoint]
    Checkpoint1 --> Step2[Step 2: Implementation Planning]

    Step2 --> Agent2[Activate Agent:<br/>requirements-analyst]
    Agent2 --> Execute2[Execute Step 2<br/>with Step 1 Outputs]
    Execute2 --> Update2[Update TodoWrite: ✅]

    Update2 --> Step3[Step 3: Code Implementation]

    Step3 --> LoadMode3[Load Mode:<br/>Parallel_Orchestration]
    LoadMode3 --> Parallel{Parallel<br/>Capable?}

    Parallel -->|Yes| Multi[Launch Multiple Agents<br/>in Parallel]
    Parallel -->|No| Single[Sequential Execution]

    Multi --> Sync[Synchronize Results]
    Single --> Sync

    Sync --> Update3[Update TodoWrite: ✅]

    Update3 --> Step4[Step 4: Code Review]
    Step4 --> QualityGate{Quality Gate}

    QualityGate -->|Fail| Block["❌ Block Progression<br/>Report Issues<br/>Request Fixes"]
    QualityGate -->|Pass| Update4[Update TodoWrite: ✅]

    Block --> Remediate[Fix Issues]
    Remediate --> QualityGate

    Update4 --> MoreSteps{More<br/>Steps?}

    MoreSteps -->|Yes| NextStep[Continue to Next Step]
    MoreSteps -->|No| CheckSuccess{All Success<br/>Criteria Met?}

    NextStep --> Step1

    CheckSuccess -->|No| Incomplete[❌ Workflow Incomplete<br/>Report Missing Criteria]
    CheckSuccess -->|Yes| Report[Generate Final Report]

    Report --> Archive[Archive Outputs]
    Archive --> Complete([✅ Workflow Complete])

    style Start fill:#e1f5ff
    style Complete fill:#c8e6c9
    style QualityGate fill:#fff3e1
    style Block fill:#ffcdd2
    style Archive fill:#c8e6c9
```

---

## Refactoring Example: End-to-End

```mermaid
graph TB
    subgraph "User Action"
        U1["User: /refactor:analyze src/auth"]
    end

    subgraph "Command Layer"
        C1["Command: refactor:analyze"]
        C2["Parse arguments:<br/>path = 'src/auth'<br/>focus = 'all'"]
    end

    subgraph "Mode Activation"
        M1["Activate: Deep_Analysis<br/>- Reasoning depth: ~32K tokens<br/>- Transparency markers on"]
        M2["Activate: Quality_Focus<br/>- Review threshold: 8/10<br/>- Coverage target: 90%"]
    end

    subgraph "Workflow Execution"
        W1["Load: refactoring.yaml"]
        W2["Step 1: Code Analysis<br/>Agent: code-reviewer"]
        W3["Step 2: Impact Assessment<br/>MCP: Codanna analyze_impact"]
        W4["Step 3: Refactoring Plan<br/>Mode: Deep_Analysis"]
    end

    subgraph "Agent Layer"
        A1["code-reviewer:<br/>- Complexity: 12 → target 6<br/>- Duplication: 45% → target 15%<br/>- Code smells: 8 found"]
        A2["Codanna MCP:<br/>- Dependencies: 23 files<br/>- Risk score: 6.5/10<br/>- Change radius: Medium"]
        A3["Planning:<br/>- Priority matrix generated<br/>- 3 quick wins identified<br/>- Migration strategy defined"]
    end

    subgraph "Output"
        O1["📄 Refactoring Plan:<br/>- Issues prioritized<br/>- Impact assessed<br/>- Recommendations clear<br/>- Safety validated"]
    end

    subgraph "Next Action"
        N1["User: /refactor:execute plan.md"]
        N2["Command: refactor:execute<br/>Mode: Parallel_Orchestration"]
        N3["Incremental Execution:<br/>- Change 1 → Test → ✅ Commit<br/>- Change 2 → Test → ✅ Commit<br/>- Change 3 → Test → ✅ Commit"]
        N4["Quality Gates:<br/>- Review: 8.5/10 ✅<br/>- Coverage: 87% ✅<br/>- Performance: +2% ✅"]
        N5["✅ Refactoring Complete"]
    end

    U1 --> C1
    C1 --> C2
    C2 --> M1
    C2 --> M2
    M1 --> W1
    M2 --> W1
    W1 --> W2
    W2 --> W3
    W3 --> W4
    W2 --> A1
    W3 --> A2
    W4 --> A3
    A1 --> O1
    A2 --> O1
    A3 --> O1
    O1 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5

    style U1 fill:#e1f5ff
    style M1 fill:#fff3e1
    style M2 fill:#fff3e1
    style O1 fill:#c8e6c9
    style N5 fill:#c8e6c9
```

---

## Decision Tree: Which Layer to Use?

```mermaid
flowchart TD
    Start{What do you<br/>need to do?}

    Start -->|Quick action| Q1{Specific<br/>task?}
    Start -->|Change behavior| Q2{How Claude<br/>operates?}
    Start -->|Multi-step process| Q3{Complex<br/>workflow?}

    Q1 -->|Yes| UseCommand["✅ Use Slash Command<br/>Example:<br/>/refactor:analyze<br/>/test:generate-tests<br/>/docs:generate"]

    Q2 -->|Reasoning depth| UseMode1["✅ Use Mode<br/>Deep_Analysis<br/>--ultrathink"]
    Q2 -->|Quality standards| UseMode2["✅ Use Mode<br/>Quality_Focus<br/>--focus quality"]
    Q2 -->|Communication style| UseMode3["✅ Use Mode<br/>Token_Efficient<br/>--uc"]
    Q2 -->|Execution pattern| UseMode4["✅ Use Mode<br/>Parallel_Orchestration<br/>--orchestrate"]

    Q3 -->|Feature development| UseWorkflow1["✅ Use Workflow<br/>/workflow:run<br/>feature-development"]
    Q3 -->|Code refactoring| UseWorkflow2["✅ Use Workflow<br/>/workflow:run<br/>refactoring"]
    Q3 -->|API design| UseWorkflow3["✅ Use Workflow<br/>/workflow:run<br/>api-design"]
    Q3 -->|Developer onboarding| UseWorkflow4["✅ Use Workflow<br/>/workflow:run<br/>onboarding"]

    UseCommand --> Examples1["Commands are:<br/>✓ Fast<br/>✓ Focused<br/>✓ Single purpose"]
    UseMode1 --> Examples2["Modes are:<br/>✓ Behavioral<br/>✓ Persistent<br/>✓ Context-aware"]
    UseMode2 --> Examples2
    UseMode3 --> Examples2
    UseMode4 --> Examples2
    UseWorkflow1 --> Examples3["Workflows are:<br/>✓ Multi-step<br/>✓ Coordinated<br/>✓ Progressive"]
    UseWorkflow2 --> Examples3
    UseWorkflow3 --> Examples3
    UseWorkflow4 --> Examples3

    Examples1 --> Combine{Can be<br/>combined?}
    Examples2 --> Combine
    Examples3 --> Combine

    Combine -->|Yes| Combined["✅ Example:<br/>/workflow:run refactoring<br/>└─ Activates: Deep_Analysis<br/>└─ Activates: Quality_Focus<br/>└─ Executes: 10 workflow steps<br/>└─ Uses: code-reviewer agent"]

    style Start fill:#e1f5ff
    style UseCommand fill:#ffe1e1
    style UseMode1 fill:#fff3e1
    style UseMode2 fill:#fff3e1
    style UseMode3 fill:#fff3e1
    style UseMode4 fill:#fff3e1
    style UseWorkflow1 fill:#e8f5e9
    style UseWorkflow2 fill:#e8f5e9
    style UseWorkflow3 fill:#e8f5e9
    style UseWorkflow4 fill:#e8f5e9
    style Combined fill:#c8e6c9
```

---

## System Statistics

```mermaid
pie title System Components Distribution
    "Slash Commands" : 43
    "Modes" : 8
    "Workflows" : 9
    "Agents" : 25
    "MCP Servers" : 3
```

```mermaid
graph LR
    subgraph "Coverage"
        A[16 Command Namespaces]
        B[8 Behavioral Modes]
        C[9 Workflow Types]
        D[25+ Specialized Agents]
        E[3 MCP Servers]
    end

    style A fill:#ffe1e1
    style B fill:#fff3e1
    style C fill:#e8f5e9
    style D fill:#f3e5f5
    style E fill:#e1f5ff
```

---

## Mode + Workflow Compatibility Matrix

```mermaid
graph TB
    subgraph "Workflows"
        W1[Feature Dev]
        W2[Bug Fix]
        W3[Refactoring]
        W4[API Design]
        W5[Tech Debt]
        W6[Arch Review]
        W7[Onboarding]
        W8[Security]
        W9[Performance]
    end

    subgraph "Modes"
        M1[Brainstorm]
        M2[Deep Analysis]
        M3[Quality Focus]
        M4[Parallel Orch]
        M5[Task Mgmt]
    end

    M1 -.-> W1
    M1 -.-> W4
    M1 -.-> W7

    M2 -.-> W3
    M2 -.-> W5
    M2 -.-> W6

    M3 -.-> W3
    M3 -.-> W5
    M3 -.-> W8

    M4 -.-> W1
    M4 -.-> W3
    M4 -.-> W4

    M5 -.-> W1
    M5 -.-> W7

    style W1 fill:#e8f5e9
    style W2 fill:#e8f5e9
    style W3 fill:#e8f5e9
    style W4 fill:#e8f5e9
    style W5 fill:#e8f5e9
    style W6 fill:#e8f5e9
    style W7 fill:#e8f5e9
    style W8 fill:#e8f5e9
    style W9 fill:#e8f5e9
    style M1 fill:#fff3e1
    style M2 fill:#fff3e1
    style M3 fill:#fff3e1
    style M4 fill:#fff3e1
    style M5 fill:#fff3e1
```

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 👤 | User / Human Input |
| 🎨 | Behavioral Mode |
| 🔄 | Workflow / Process |
| 🤖 | Agent / AI Actor |
| 🔌 | MCP Server |
| 🛠️ | Native Tool |
| ✅ | Success / Complete |
| ❌ | Failure / Error |
| 📋 | Task / Todo |
| 📄 | Output / Document |
| ⚡ | Fast / Optimized |
| 🔒 | Security |
| 🎯 | Target / Goal |

---

## Quick Start Guide

### For Developers

1. **Explore the system**:

   ```bash
   cortex
   # Press 3 → View Modes
   # Press 6 → View Workflows
   ```

2. **Try a command**:

   ```bash
   /refactor:analyze src/
   /workflow:run feature-development
   /mode:activate Brainstorm
   ```

3. **Understand the flow**:
   - Command activates → Mode influences → Workflow executes → Agents work

### For Architects

1. **Review diagrams** in this file
2. **Understand three layers**: Commands → Modes → Workflows
3. **Study integration patterns**: How layers interact
4. **Customize workflows**: Adapt to your needs

### For DevOps

1. **Deployment workflows**: `feature-development`, `security-audit`
2. **Quality gates**: Integrated in all workflows
3. **Automation ready**: Commands can be scripted
4. **State management**: Checkpoint/resume support
