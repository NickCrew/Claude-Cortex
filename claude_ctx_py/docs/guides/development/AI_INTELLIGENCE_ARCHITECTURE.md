# AI Intelligence System: Technical Architecture

**Version**: 1.0  
**Last Updated**: 2025-12-05  
**Status**: Current

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Pattern Learning System](#pattern-learning-system)
5. [Skill Recommendation Engine](#skill-recommendation-engine)
6. [Context Detection](#context-detection)
7. [Auto-Activation System](#auto-activation-system)
8. [Data Models](#data-models)
9. [Machine Learning Approach](#machine-learning-approach)
10. [CLI Commands](#cli-commands)
11. [TUI Integration](#tui-integration)
12. [Development Guide](#development-guide)

---

## Overview

### Purpose

The **AI Intelligence System** provides autonomous, learning-based automation that:
- ✅ Predicts which agents/skills are needed based on context
- ✅ Learns from successful sessions to improve recommendations
- ✅ Auto-activates high-confidence recommendations
- ✅ Detects workflow patterns and predicts optimal sequences
- ✅ Provides intelligent skill suggestions based on file changes

### Key Characteristics

- **Pattern Learning**: Learns from historical session data
- **Context-Aware**: Analyzes files, directories, and code signals
- **Multi-Strategy**: Rule-based + Pattern-based + Agent-based recommendations
- **Confidence-Scored**: All recommendations include confidence metrics (0.0-1.0)
- **Auto-Activation**: High-confidence recommendations auto-activate (≥80% confidence)
- **Feedback Loop**: Improves from user feedback via SQLite storage

### Design Philosophy

```
Learn > Predict > Automate | Context > Rules | Confidence > Authority
```

The system prioritizes **learning from real usage** over hardcoded rules, **context detection** over static config, and **probabilistic confidence** over binary decisions.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│ User Interface Layer                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CLI Commands              TUI View (Key 0)             │
│  ├─ ai recommend           ├─ Recommendations           │
│  ├─ ai auto-activate       ├─ Auto-activation           │
│  ├─ ai record-success      ├─ Workflow predictions      │
│  └─ ai export              └─ Context analysis          │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ Intelligence Layer                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  IntelligentAgent          SkillRecommender             │
│  ├─ Context analysis       ├─ Rule-based recs           │
│  ├─ Recommendations        ├─ Agent-based recs          │
│  ├─ Auto-activation        ├─ Pattern-based recs        │
│  └─ Session recording      └─ Feedback learning         │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ Learning Layer                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  PatternLearner            ContextDetector              │
│  ├─ Pattern storage        ├─ File analysis             │
│  ├─ Agent prediction       ├─ Git integration           │
│  ├─ Workflow prediction    └─ Signal detection          │
│  └─ Success recording                                   │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ Data Layer                                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ~/.claude/intelligence/                                │
│  ├─ session_history.json   → Pattern learning data     │
│  └─ recommendation-rules.json → Rule definitions        │
│                                                          │
│  ~/.claude/data/                                         │
│  └─ skill-recommendations.db → SQLite feedback DB       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow: Making a Recommendation

```
1. Context Detection
   └─ ContextDetector.detect_from_files(changed_files)
      ├─ Analyze file types (.py, .ts, .tf, etc.)
      ├─ Detect patterns (auth, api, tests, db)
      └─ Build SessionContext

2. Pattern Matching
   └─ PatternLearner.predict_agents(context)
      ├─ Generate context_key (e.g., "backend_api_tests")
      ├─ Find similar historical sessions
      ├─ Count agent frequency in similar contexts
      └─ Create pattern-based recommendations

3. Rule-Based Enrichment
   └─ _rule_based_recommendations(context)
      ├─ If has_auth → recommend security-auditor (0.9)
      ├─ If test_failures → recommend test-automator (0.95)
      ├─ If changeset → recommend quality-engineer (0.85)
      ├─ If changeset → recommend code-reviewer (0.75)
      ├─ If TS/TSX → recommend typescript-pro (0.85)
      ├─ If React/JSX/TSX → recommend react-specialist (0.8)
      ├─ If UI changes → recommend ui-ux-designer (0.8)
      ├─ If DB/SQL → recommend database-optimizer, sql-pro (0.8)
      ├─ If cross-cutting → recommend architect-review (0.75)
      └─ Merge with pattern recommendations

4. Confidence Scoring
   └─ Sort recommendations by confidence
      ├─ confidence >= 0.8 → auto_activate = true
      ├─ confidence >= 0.7 → urgency = "high"
      └─ confidence >= 0.3 → include in results

5. Return Recommendations
   └─ List[AgentRecommendation] sorted by confidence
```

---

## Core Components

### 1. IntelligentAgent (Main Orchestrator)

**Location**: `intelligence.py` - `IntelligentAgent` class

The central controller for all AI features:

```python
class IntelligentAgent:
    """Main intelligent automation agent."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.learner = PatternLearner(data_dir / "session_history.json")
        self.context_detector = ContextDetector()
        self.current_context: Optional[SessionContext] = None
        self.recommendations: List[AgentRecommendation] = []
        self.auto_activated: Set[str] = set()
```

**Key Methods**:

**analyze_context()** - Analyze current working context
```python
def analyze_context(self, files: Optional[List[Path]] = None) -> SessionContext:
    """Analyze current context from files or git."""
    if files is None:
        files = self.context_detector.detect_from_git()
    
    self.current_context = self.context_detector.detect_from_files(files)
    return self.current_context
```

**get_recommendations()** - Get intelligent recommendations
```python
def get_recommendations(self) -> List[AgentRecommendation]:
    """Get recommendations for current context."""
    if self.current_context is None:
        self.analyze_context()
    
    self.recommendations = self.learner.predict_agents(self.current_context)
    return self.recommendations
```

**get_auto_activations()** - Get agents to auto-activate
```python
def get_auto_activations(self) -> List[str]:
    """Get list of agents that should be auto-activated."""
    recommendations = self.get_recommendations()
    return [
        rec.agent_name
        for rec in recommendations
        if rec.auto_activate and rec.agent_name not in self.auto_activated
    ]
```

**record_session_success()** - Record successful session for learning
```python
def record_session_success(
    self,
    agents_used: List[str],
    duration: int,
    outcome: str = "success"
) -> None:
    """Record successful session to improve future predictions."""
    if self.current_context is not None:
        self.learner.record_success(
            self.current_context,
            agents_used,
            duration,
            outcome,
        )
```

### 2. SessionContext (Context Model)

**Location**: `intelligence.py` - `SessionContext` dataclass

Captures all relevant context for intelligent decision-making:

```python
@dataclass
class SessionContext:
    """Represents current session context."""
    
    # File context
    files_changed: List[str]
    file_types: Set[str]              # {".py", ".ts", ".go"}
    directories: Set[str]              # Changed directories
    
    # Code context signals
    has_tests: bool                    # Test files detected
    has_auth: bool                     # Auth code detected
    has_api: bool                      # API/routes detected
    has_frontend: bool                 # Frontend files (.tsx, .vue)
    has_backend: bool                  # Backend files (.py, .go)
    has_database: bool                 # Database/schema files
    
    # Activity context
    errors_count: int
    test_failures: int
    build_failures: int
    
    # Time context
    session_start: datetime
    last_activity: datetime
    
    # Current state
    active_agents: List[str]
    active_modes: List[str]
    active_rules: List[str]
```

**Context Key Generation**:
```python
# Example: Context with backend API and tests
# Generates key: "api_backend_tests"
def _generate_context_key(self, context: SessionContext) -> str:
    components = []
    if context.has_frontend: components.append("frontend")
    if context.has_backend: components.append("backend")
    if context.has_database: components.append("database")
    if context.has_tests: components.append("tests")
    if context.has_auth: components.append("auth")
    if context.has_api: components.append("api")
    
    return "_".join(sorted(components)) or "general"
```

### 3. AgentRecommendation (Recommendation Model)

**Location**: `intelligence.py` - `AgentRecommendation` dataclass

Represents a single agent recommendation with metadata:

```python
@dataclass
class AgentRecommendation:
    """Intelligent agent recommendation."""
    
    agent_name: str                    # "security-auditor"
    confidence: float                  # 0.0-1.0 (0.9 = 90%)
    reason: str                        # "Auth code detected"
    urgency: str                       # "low", "medium", "high", "critical"
    auto_activate: bool                # True if confidence >= 0.8
    context_triggers: List[str]        # ["auth_code", "backend"]
    
    def should_notify(self) -> bool:
        """Should this notify the user?"""
        return self.confidence >= 0.7 or self.urgency in ("high", "critical")
```

**Example Recommendation**:
```python
AgentRecommendation(
    agent_name="security-auditor",
    confidence=0.9,
    reason="Auth code detected - security review recommended",
    urgency="high",
    auto_activate=True,
    context_triggers=["auth_code"]
)
```

---

## Pattern Learning System

### PatternLearner Class

**Location**: `intelligence.py` - `PatternLearner` class

Learns from historical sessions to predict future needs:

```python
class PatternLearner:
    """Learns patterns from successful sessions."""
    
    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.agent_sequences: List[List[str]] = []
        self.success_contexts: List[Dict] = []
        self._load_history()
```

### Learning Algorithm

**Step 1: Record Success**
```python
def record_success(
    self,
    context: SessionContext,
    agents_used: List[str],
    duration: int,
    outcome: str,
) -> None:
    """Record successful session for learning."""
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "context": context.to_dict(),
        "agents": agents_used,
        "duration": duration,
        "outcome": outcome,
    }
    
    # Store by context type
    context_key = self._generate_context_key(context)
    self.patterns[context_key].append(session_data)
    
    # Store agent sequence
    self.agent_sequences.append(agents_used)
    
    # Persist to disk
    self._save_history()
```

**Step 2: Predict Agents**
```python
def predict_agents(self, context: SessionContext) -> List[AgentRecommendation]:
    """Predict agents based on similar historical sessions."""
    recommendations = []
    context_key = self._generate_context_key(context)
    
    # Get similar sessions
    similar_sessions = self.patterns.get(context_key, [])
    
    if similar_sessions:
        # Count agent frequency
        agent_counts: Counter[str] = Counter()
        for session in similar_sessions:
            agent_counts.update(session["agents"])
        
        total_sessions = len(similar_sessions)
        
        # Recommend if used in >30% of similar sessions
        for agent, count in agent_counts.most_common(10):
            confidence = count / total_sessions
            
            if confidence >= 0.3:
                recommendation = AgentRecommendation(
                    agent_name=agent,
                    confidence=confidence,
                    reason=f"Used in {count}/{total_sessions} similar sessions",
                    urgency="medium" if confidence >= 0.7 else "low",
                    auto_activate=confidence >= 0.8,
                    context_triggers=[context_key],
                )
                recommendations.append(recommendation)
    
    return recommendations
```

**Step 3: Predict Workflow**
```python
def predict_workflow(self, context: SessionContext) -> Optional[WorkflowPrediction]:
    """Predict optimal workflow based on historical patterns."""
    context_key = self._generate_context_key(context)
    similar_sessions = self.patterns.get(context_key, [])
    
    if len(similar_sessions) < 3:
        return None  # Need at least 3 sessions
    
    # Find most common agent sequence
    sequence_counts: Counter[Tuple[str, ...]] = Counter()
    for session in similar_sessions:
        seq_key = tuple(session["agents"])
        sequence_counts[seq_key] += 1
    
    most_common_seq, count = sequence_counts.most_common(1)[0]
    confidence = count / len(similar_sessions)
    
    # Calculate average duration
    durations = [
        s["duration"] for s in similar_sessions
        if tuple(s["agents"]) == most_common_seq
    ]
    avg_duration = int(sum(durations) / len(durations)) if durations else 600
    
    return WorkflowPrediction(
        workflow_name=f"auto_{context_key}",
        agents_sequence=list(most_common_seq),
        confidence=confidence,
        estimated_duration=avg_duration,
        success_probability=confidence,
        based_on_pattern=context_key,
    )
```

### Storage Format

**session_history.json**:
```json
{
  "patterns": {
    "backend_api_tests": [
      {
        "timestamp": "2025-12-05T14:30:00",
        "context": {
          "files_changed": ["api/routes.py", "tests/test_api.py"],
          "file_types": [".py"],
          "has_backend": true,
          "has_api": true,
          "has_tests": true
        },
        "agents": ["python-pro", "test-automator", "api-documenter"],
        "duration": 1800,
        "outcome": "success"
      }
    ]
  },
  "agent_sequences": [
    ["python-pro", "test-automator"],
    ["security-auditor", "code-reviewer"]
  ],
  "success_contexts": [...],
  "last_updated": "2025-12-05T15:00:00"
}
```

---

## Skill Recommendation Engine

### SkillRecommender Class

**Location**: `skill_recommender.py` - `SkillRecommender` class

Recommends skills based on multi-strategy analysis:

```python
class SkillRecommender:
    """AI-powered skill recommendation engine."""
    
    def __init__(self, home: Path | None = None):
        self.home = _resolve_claude_dir(home)
        self.db_path = self.home / "data" / "skill-recommendations.db"
        self.rules_path = self.home / "skills" / "recommendation-rules.json"
        self._init_database()
        self._load_rules()
```

### Recommendation Strategies

**Strategy 1: Rule-Based**

File patterns trigger skill recommendations:

```python
# recommendation-rules.json
{
  "rules": [
    {
      "trigger": {
        "file_patterns": ["**/auth/**/*.py", "**/security/**"]
      },
      "recommend": [
        {
          "skill": "owasp-top-10",
          "confidence": 0.9,
          "reason": "Auth code detected, security review recommended"
        }
      ]
    }
  ]
}
```

**Strategy 2: Agent-Based**

Active agents trigger related skills:

```python
AGENT_SKILL_MAP = {
    "security-auditor": [
        ("owasp-top-10", 0.95),
        ("threat-modeling-techniques", 0.9),
        ("secure-coding-practices", 0.85),
    ],
    "kubernetes-architect": [
        ("kubernetes-deployment-patterns", 0.95),
        ("helm-chart-patterns", 0.9),
    ],
    "python-pro": [
        ("python-testing-patterns", 0.9),
        ("async-python-patterns", 0.85),
    ],
}
```

**Strategy 3: Pattern-Based**

Historical success patterns inform recommendations:

```python
def _pattern_based_recommendations(
    self,
    context: SessionContext
) -> List[SkillRecommendation]:
    """Generate recommendations based on historical success."""
    # Query database for similar contexts
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("""
            SELECT successful_skills, success_rate
            FROM context_patterns
            WHERE success_rate > 0.7
            ORDER BY last_updated DESC
            LIMIT 10
        """)
        
        skill_scores: Counter[str] = Counter()
        for row in cursor.fetchall():
            skills = json.loads(row[0])
            success_rate = row[1]
            for skill in skills:
                skill_scores[skill] += success_rate
    
    # Create recommendations from top scoring skills
    recommendations = []
    for skill_name, score in skill_scores.most_common(5):
        confidence = min(0.8, score / 10)
        if confidence >= 0.6:
            recommendations.append(SkillRecommendation(
                skill_name=skill_name,
                confidence=confidence,
                reason="Successful in similar projects",
                triggers=["historical_pattern"],
                related_agents=[],
                estimated_value="high" if confidence >= 0.7 else "medium",
                auto_activate=False
            ))
    
    return recommendations
```

### Database Schema

**SQLite Database**: `~/.claude/data/skill-recommendations.db`

```sql
-- Recommendations history
CREATE TABLE recommendations_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    context_hash TEXT NOT NULL,
    was_activated BOOLEAN DEFAULT 0,
    was_helpful BOOLEAN NULL,
    reason TEXT
);

-- User feedback
CREATE TABLE recommendation_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id INTEGER,
    timestamp TEXT NOT NULL,
    helpful BOOLEAN NOT NULL,
    comment TEXT,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations_history(id)
);

-- Context patterns for learning
CREATE TABLE context_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context_hash TEXT UNIQUE NOT NULL,
    file_patterns TEXT,         -- JSON array
    active_agents TEXT,          -- JSON array
    successful_skills TEXT,      -- JSON array
    success_rate REAL,
    last_updated TEXT
);
```

### Feedback Loop

**Recording Feedback**:
```python
def learn_from_feedback(
    self,
    skill: str,
    was_helpful: bool,
    context_hash: str,
    comment: Optional[str] = None
) -> None:
    """Update model based on user feedback."""
    with sqlite3.connect(self.db_path) as conn:
        # Find the recommendation
        cursor = conn.execute("""
            SELECT id FROM recommendations_history
            WHERE skill_name = ? AND context_hash = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (skill, context_hash))
        
        row = cursor.fetchone()
        if row:
            # Update recommendation
            conn.execute("""
                UPDATE recommendations_history
                SET was_helpful = ?
                WHERE id = ?
            """, (was_helpful, row[0]))
            
            # Insert feedback
            conn.execute("""
                INSERT INTO recommendation_feedback
                (recommendation_id, timestamp, helpful, comment)
                VALUES (?, ?, ?, ?)
            """, (row[0], datetime.now().isoformat(), was_helpful, comment))
            
            conn.commit()
```

---

## Context Detection

### ContextDetector Class

**Location**: `intelligence.py` - `ContextDetector` class

Detects context from file system and git:

```python
class ContextDetector:
    """Detects context from file system and code analysis."""
    
    @staticmethod
    def detect_from_files(files: List[Path]) -> SessionContext:
        """Detect context from file list."""
        file_types = set()
        directories = set()
        files_changed = []
        
        # Analyze files
        for file_path in files:
            files_changed.append(str(file_path))
            file_types.add(file_path.suffix.lower())
            directories.add(str(file_path.parent))
        
        # Detect signals
        has_tests = any("test" in str(f).lower() for f in files)
        has_auth = any("auth" in str(f).lower() for f in files)
        has_api = any("api" in str(f).lower() or "routes" in str(f).lower() 
                      for f in files)
        has_frontend = any(ext in file_types 
                           for ext in {".tsx", ".jsx", ".vue", ".html"})
        has_backend = any(ext in file_types 
                          for ext in {".py", ".go", ".java", ".rs"})
        has_database = any("db" in str(f).lower() or "schema" in str(f).lower() 
                           for f in files)
        
        return SessionContext(
            files_changed=files_changed,
            file_types=file_types,
            directories=directories,
            has_tests=has_tests,
            has_auth=has_auth,
            has_api=has_api,
            has_frontend=has_frontend,
            has_backend=has_backend,
            has_database=has_database,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )
```

### Git Integration

```python
@staticmethod
def detect_from_git() -> List[Path]:
    """Detect changed files from git."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    files = [
        Path(line.strip()) 
        for line in result.stdout.split("\n") 
        if line.strip()
    ]
    
    return files
```

### Signal Detection Logic

| Signal | Detection Logic |
|--------|----------------|
| `has_tests` | "test" in filename (case-insensitive) |
| `has_auth` | "auth" in filename or path |
| `has_api` | "api" or "routes" in filename/path |
| `has_frontend` | File extension in {.tsx, .jsx, .vue, .svelte, .html, .css} |
| `has_backend` | File extension in {.py, .go, .java, .rs, .rb} |
| `has_database` | "db", "migration", or "schema" in filename/path |

---

## Auto-Activation System

### Auto-Activation Logic

```python
def get_auto_activations(self) -> List[str]:
    """Get list of agents that should be auto-activated."""
    recommendations = self.get_recommendations()
    
    return [
        rec.agent_name
        for rec in recommendations
        if rec.auto_activate and rec.agent_name not in self.auto_activated
    ]
```

### Activation Criteria

An agent is auto-activated if **ALL** of the following are true:
- ✅ Confidence >= 0.8 (80%)
- ✅ Not already auto-activated this session
- ✅ Urgency is "high" or "critical" (for rule-based recs)

### Example: Auto-Activation Workflow

```
1. Context Detection
   └─ Files: ["src/auth.py", "src/security.py"]
   └─ Signal: has_auth = true

2. Generate Recommendations
   └─ security-auditor: confidence=0.9, auto_activate=true

3. Check Auto-Activation
   └─ confidence >= 0.8? YES
   └─ already activated? NO
   └─ Result: AUTO-ACTIVATE

4. Activate Agent
   └─ agent_activate("security-auditor")
   └─ Mark as auto-activated in session
   └─ Notify user: "✓ Auto-activated: security-auditor"
```

### CLI Usage

```bash
# Analyze context and auto-activate high-confidence recommendations
$ cortex ai auto-activate

🤖 Auto-activating 2 agents...

✓ security-auditor
✓ test-automator

✓ Activated 2/2 agents
```

---

## Data Models

### Core Data Models

**SessionContext**:
```python
@dataclass
class SessionContext:
    files_changed: List[str]
    file_types: Set[str]
    directories: Set[str]
    has_tests: bool
    has_auth: bool
    has_api: bool
    has_frontend: bool
    has_backend: bool
    has_database: bool
    errors_count: int
    test_failures: int
    build_failures: int
    session_start: datetime
    last_activity: datetime
    active_agents: List[str]
    active_modes: List[str]
    active_rules: List[str]
```

**AgentRecommendation**:
```python
@dataclass
class AgentRecommendation:
    agent_name: str
    confidence: float          # 0.0-1.0
    reason: str
    urgency: str              # low|medium|high|critical
    auto_activate: bool
    context_triggers: List[str]
```

**SkillRecommendation**:
```python
@dataclass
class SkillRecommendation:
    skill_name: str
    confidence: float          # 0.0-1.0
    reason: str
    triggers: List[str]
    related_agents: List[str]
    estimated_value: str       # high|medium|low
    auto_activate: bool
```

**WorkflowPrediction**:
```python
@dataclass
class WorkflowPrediction:
    workflow_name: str
    agents_sequence: List[str]
    confidence: float
    estimated_duration: int    # seconds
    success_probability: float
    based_on_pattern: str
```

---

## Machine Learning Approach

### Algorithm: Collaborative Filtering

The system uses a **frequency-based collaborative filtering** approach:

```
1. Session Recording
   └─ When session is successful, record:
      ├─ Context (files, signals, agents)
      ├─ Agents used
      ├─ Duration
      └─ Outcome

2. Pattern Extraction
   └─ Group sessions by context_key
   └─ Example: "backend_api_tests" → [session1, session2, ...]

3. Frequency Analysis
   └─ For each context_key:
      ├─ Count agent usage
      └─ Calculate: confidence = count / total_sessions

4. Prediction
   └─ Given new context:
      ├─ Generate context_key
      ├─ Find similar sessions
      ├─ Recommend agents with confidence >= 0.3
      └─ Auto-activate if confidence >= 0.8
```

### Confidence Scoring

**Pattern-Based Confidence**:
```python
confidence = agent_usage_count / total_similar_sessions

# Example:
# Total sessions with "backend_api" context: 10
# Sessions using "python-pro": 8
# Confidence for "python-pro": 8/10 = 0.8 (80%)
```

**Rule-Based Confidence**: Hardcoded based on signal strength
- Auth code detected → security-auditor (0.9)
- Test failures → test-automator (0.95)
- Any changeset → quality-engineer (0.85)
- Any changeset → code-reviewer (0.75)
- TypeScript/TSX → typescript-pro (0.85)
- React/JSX/TSX → react-specialist (0.8)
- User-facing UI → ui-ux-designer (0.8)
- Database/SQL → database-optimizer, sql-pro (0.8)
- Cross-cutting changes → architect-review (0.75)

**Combined Confidence**: When multiple strategies recommend same agent
```python
# Base confidence from strategy 1: 0.75
# Boost from strategy 2: +0.05
# Boost from strategy 3: +0.03
# Final confidence: min(0.99, 0.75 + 0.05 + 0.03) = 0.83
```

### Learning Rate

The system improves over time:
- **Cold Start** (0-5 sessions): Relies on rule-based recommendations
- **Warm** (5-20 sessions): Mix of rules + basic patterns
- **Hot** (20+ sessions): Strong pattern-based predictions

---

## CLI Commands

### ai recommend

Show AI recommendations for current context:

```bash
$ cortex ai recommend

🤖 AI RECOMMENDATIONS

══════════════════════════════════════════════════════════════════

1. 🔴 security-auditor [AUTO]
   Confidence: 90%
   Reason: Auth code detected - security review recommended

2. 🔵 quality-engineer [AUTO]
   Confidence: 85%
   Reason: Changes detected - quality review recommended

3. 🔵 code-reviewer [AUTO]
   Confidence: 75%
   Reason: Changes detected - code review recommended

4. 🔵 performance-engineer [AUTO]
   Confidence: 70%
   Reason: Performance-sensitive changes detected

══════════════════════════════════════════════════════════════════

🎯 WORKFLOW PREDICTION

Workflow: auto_backend_api_auth
Confidence: 80%
Estimated Duration: 15m 30s
Success Probability: 80%

Agent Sequence:
  1. security-auditor
  2. python-pro
  3. test-automator

══════════════════════════════════════════════════════════════════

📊 CONTEXT ANALYSIS

Files Changed: 7
Detected: Backend, API, Auth

══════════════════════════════════════════════════════════════════

💡 TIP: Press '0' in the TUI for interactive AI assistant
        Press 'A' to auto-activate recommended agents
```

### ai auto-activate

Auto-activate high-confidence recommendations:

```bash
$ cortex ai auto-activate

🤖 Auto-activating 2 agents...

✓ security-auditor
✓ test-automator

✓ Activated 2/2 agents
```

### ai record-success

Record successful session for learning:

```bash
$ cortex ai record-success "all tests passing"

✓ Recorded successful session for learning
  Context: 7 files changed
  Agents: security-auditor, python-pro, test-automator
  Outcome: all tests passing

💡 This session will improve future recommendations!
```

### ai export

Export recommendations to JSON:

```bash
$ cortex ai export --output recommendations.json

✓ Exported AI recommendations to recommendations.json
  3 agent recommendations
  1 workflow prediction (80% confidence)
```

**Output Format**:
```json
{
  "agent_recommendations": [
    {
      "agent": "security-auditor",
      "confidence": "90%",
      "reason": "Auth code detected",
      "urgency": "high",
      "auto_activate": true
    }
  ],
  "workflow_prediction": {
    "name": "auto_backend_api_auth",
    "agents": ["security-auditor", "python-pro"],
    "confidence": "80%",
    "estimated_time": "15m 30s"
  },
  "context": {
    "files_changed": 7,
    "has_tests": true,
    "has_auth": true,
    "has_api": true
  }
}
```

---

## TUI Integration

### AI Assistant View (Key: 0)

**Location**: `tui/main.py` - AI Assistant view implementation

**Features**:
- 📊 Real-time context analysis
- 🤖 Agent recommendations with confidence scores
- 🎯 Workflow predictions
- ⚡ One-click auto-activation
- 📈 Learning statistics

**Keyboard Navigation**:
```
0          → Open AI Assistant view
Enter      → Auto-activate selected recommendation
a          → Auto-activate all high-confidence recs
r          → Refresh recommendations
s          → Record session success
c          → Export to clipboard
Esc        → Close view
```

**View Layout**:
```
┌──────────────────────────────────────────────────────┐
│ 🤖 AI ASSISTANT                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ CONTEXT ANALYSIS                                     │
│ Files: 7 | Backend, API, Auth                       │
│                                                      │
│ RECOMMENDATIONS                                      │
│ ├─ 🔴 security-auditor (90%) [AUTO]                 │
│ ├─ 🟡 test-automator (75%)                          │
│ └─ 🔵 code-reviewer (65%)                           │
│                                                      │
│ WORKFLOW PREDICTION                                  │
│ auto_backend_api_auth (80% confidence)               │
│ Sequence: security-auditor → python-pro → ...       │
│                                                      │
│ [A] Auto-Activate | [R] Refresh | [S] Record        │
└──────────────────────────────────────────────────────┘
```

---

## Development Guide

### Adding New Context Signals

**Step 1**: Add signal to `SessionContext`:
```python
@dataclass
class SessionContext:
    # ... existing fields
    has_docker: bool          # NEW
```

**Step 2**: Update detection logic:
```python
def detect_from_files(files: List[Path]) -> SessionContext:
    # ... existing detection
    
    # NEW: Detect Docker files
    has_docker = any(
        "docker" in str(f).lower() or 
        "Dockerfile" in str(f) 
        for f in files
    )
    
    return SessionContext(
        # ... existing fields
        has_docker=has_docker,
    )
```

**Step 3**: Add to context key generation:
```python
def _generate_context_key(self, context: SessionContext) -> str:
    components = []
    # ... existing components
    if context.has_docker:
        components.append("docker")
    
    return "_".join(sorted(components)) or "general"
```

**Step 4**: Add rule-based recommendations:
```python
def _rule_based_recommendations(self, context: SessionContext) -> List:
    recommendations = []
    
    # NEW: Docker recommendations
    if context.has_docker:
        recommendations.append(
            AgentRecommendation(
                agent_name="docker-specialist",
                confidence=0.85,
                reason="Docker files detected",
                urgency="medium",
                auto_activate=False,
                context_triggers=["docker"],
            )
        )
    
    return recommendations
```

### Testing Intelligence Features

**Example Test** (`tests/unit/test_intelligence.py`):
```python
from claude_ctx_py.intelligence import (
    ContextDetector,
    PatternLearner,
    IntelligentAgent,
    SessionContext,
)
from pathlib import Path

def test_context_detection():
    """Test context detection from files."""
    files = [
        Path("src/auth.py"),
        Path("tests/test_auth.py"),
        Path("api/routes.py"),
    ]
    
    context = ContextDetector.detect_from_files(files)
    
    assert context.has_auth
    assert context.has_tests
    assert context.has_api
    assert context.has_backend
    assert ".py" in context.file_types

def test_pattern_learning(tmp_path):
    """Test pattern learning and prediction."""
    history_file = tmp_path / "history.json"
    learner = PatternLearner(history_file)
    
    # Create mock context
    context = SessionContext(
        files_changed=["src/api.py"],
        file_types={".py"},
        directories={"src"},
        has_auth=True,
        has_api=True,
        # ... other fields
    )
    
    # Record success
    learner.record_success(
        context,
        agents_used=["security-auditor", "python-pro"],
        duration=600,
        outcome="success",
    )
    
    # Verify pattern stored
    assert "auth_api" in learner.patterns or "api_auth" in learner.patterns
    
    # Test prediction
    recommendations = learner.predict_agents(context)
    assert len(recommendations) > 0
```

### Debugging Tips

**1. View session history**:
```bash
$ cat ~/.claude/intelligence/session_history.json | jq '.'
```

**2. Inspect SQLite database**:
```bash
$ sqlite3 ~/.claude/data/skill-recommendations.db

sqlite> SELECT * FROM recommendations_history LIMIT 10;
sqlite> SELECT skill_name, AVG(confidence), COUNT(*) 
        FROM recommendations_history 
        GROUP BY skill_name;
```

**3. Test context detection**:
```python
from claude_ctx_py.intelligence import ContextDetector

files = [Path("your/changed/file.py")]
context = ContextDetector.detect_from_files(files)
print(context)
```

**4. Dry-run recommendations**:
```python
from claude_ctx_py.intelligence import IntelligentAgent
from pathlib import Path

agent = IntelligentAgent(Path("~/.claude/intelligence"))
agent.analyze_context()
recommendations = agent.get_recommendations()

for rec in recommendations:
    print(f"{rec.agent_name}: {rec.confidence:.2f} - {rec.reason}")
```

---

## Performance Considerations

### Memory Usage

- **Session History**: ~1KB per recorded session
- **SQLite Database**: ~100KB for 1,000 recommendations
- **In-Memory Cache**: ~5MB for loaded patterns

### Performance Metrics

| Operation | Target | Notes |
|-----------|--------|-------|
| Context detection | <50ms | File analysis |
| Generate recommendations | <100ms | Pattern matching |
| Record session | <20ms | JSON append |
| Auto-activation | <500ms | Includes agent activation |
| SQLite query | <10ms | Indexed queries |

### Scaling Considerations

**Session History**:
- 1,000 sessions ≈ 1MB
- 10,000 sessions ≈ 10MB
- Recommend pruning after 50,000 sessions

**SQLite Database**:
- Scales to millions of rows
- Indexed on `skill_name` and `context_hash`
- Auto-vacuum enabled

---

## Related Documentation

- [Master Architecture Document](../../architecture/MASTER_ARCHITECTURE.md)
- [Memory Vault System](./MEMORY_VAULT_ARCHITECTURE.md)
- [Skill Rating System](./SKILL_RATING_ARCHITECTURE.md) (pending)
- [Watch Mode Integration](./WATCH_MODE_ARCHITECTURE.md) (pending)

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-05 | Initial AI Intelligence documentation | System Architect |

---

**Document Status**: ✅ Current  
**Maintainer**: Core Team
