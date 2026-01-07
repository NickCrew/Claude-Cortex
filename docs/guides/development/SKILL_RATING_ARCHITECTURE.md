# Skill Rating & Feedback System: Technical Architecture

**Version**: 1.0  
**Last Updated**: 2025-12-06  
**Status**: Current

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Rating System](#rating-system)
4. [Auto-Prompt System](#auto-prompt-system)
5. [Quality Metrics](#quality-metrics)
6. [Database Schema](#database-schema)
7. [TUI Integration](#tui-integration)
8. [Analytics & Reports](#analytics--reports)
9. [Privacy & Anonymity](#privacy--anonymity)
10. [CLI Commands](#cli-commands)
11. [Development Guide](#development-guide)

---

## Overview

### Purpose

**Skill Rating & Feedback System** provides community-driven quality signals through:
- ⭐ 1-5 star ratings with optional reviews
- 📊 Automated quality metrics (success rate, helpfulness %)
- 🤖 Intelligent auto-prompts after skill usage
- 📈 Analytics dashboard and top-rated leaderboard
- 🔒 Anonymous user tracking (SHA256 hash)

### Key Characteristics

- **SQLite Storage**: 3 tables (ratings, metrics, usage)
- **Auto-Prompts**: Smart timing (12hr lookback, 24hr cooldown)
- **Quality Metrics**: 6 dimensions (avg rating, success %, helpful %, token efficiency, usage count, distribution)
- **TUI Integration**: Ctrl+R shortcut in Skills view
- **Privacy-First**: Anonymous user hashing (machine ID + username)

### Design Philosophy

```
Community > Individual | Data > Opinion | Prompt > Nag | Anonymous > Identified
```

System prioritizes **aggregate community wisdom**, **measured outcomes** over subjective opinions, **smart non-intrusive prompts**, and **user privacy** through anonymization.

---

## Architecture

### System Architecture

```
┌──────────────────────────────────────────────────────────┐
│ User Interfaces                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  TUI (Ctrl+R)          CLI Commands                     │
│  ├─ Rate skill         ├─ skills rate                   │
│  ├─ View ratings       ├─ skills top-rated              │
│  └─ Review history     └─ skills export-ratings         │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ Rating Management Layer                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SkillRatingCollector                                    │
│  ├─ record_rating()    → Store rating in DB             │
│  ├─ record_usage()     → Track success correlation      │
│  ├─ get_skill_score()  → Fetch aggregated metrics       │
│  └─ _update_metrics()  → Recompute on new data          │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ Auto-Prompt Intelligence                                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SkillRatingPromptManager                                │
│  ├─ detect_due_prompts()   → Find skills needing rating │
│  ├─ mark_prompted()        → Enforce cooldown           │
│  ├─ mark_rated()           → Update state               │
│  └─ _should_prompt()       → Smart heuristics           │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ Data Layer (SQLite)                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ~/.claude/data/skill-ratings.db                        │
│  ├─ skill_ratings            → Individual ratings       │
│  ├─ skill_quality_metrics    → Aggregated cache         │
│  └─ skill_usage              → Success tracking         │
│                                                          │
│  ~/.claude/data/skill-rating-prompts.json               │
│  └─ Prompt state (last_prompted, last_rated)            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Data Flow: Rating a Skill

```
1. User Action
   └─ TUI: Press Ctrl+R on selected skill
      CLI: cortex skills rate <skill> --stars 5

2. Collect Rating Data
   └─ Stars (1-5)
   └─ Helpful? (yes/no)
   └─ Task succeeded? (yes/no)
   └─ Optional review text
   └─ Optional project type

3. Generate Anonymous User Hash
   └─ SHA256(platform.node() + getpass.getuser())
   └─ Truncate to 16 chars
   └─ Example: "a3f8d2e1c4b9f7e6"

4. Store in Database
   └─ INSERT INTO skill_ratings
   └─ Timestamp in UTC

5. Update Aggregated Metrics
   └─ Calculate avg_rating
   └─ Calculate helpful_percentage
   └─ Calculate success_correlation
   └─ Calculate star distribution
   └─ UPSERT skill_quality_metrics

6. Mark Prompted State
   └─ Update skill-rating-prompts.json
   └─ Set last_rated timestamp
   └─ Prevent duplicate prompts
```

---

## Rating System

### SkillRatingCollector Class

**Location**: `skill_rating.py` - `SkillRatingCollector`

Main API for rating operations:

```python
class SkillRatingCollector:
    """Collect and aggregate skill ratings."""
    
    def __init__(self, home: Path | None = None):
        self.home = _resolve_claude_dir(home)
        self.db_path = self.home / "data" / "skill-ratings.db"
        self._init_database()
```

### Recording Ratings

```python
def record_rating(
    self,
    skill: str,
    stars: int,              # 1-5
    helpful: bool,           # Was helpful?
    task_succeeded: bool,    # Task succeeded?
    review: Optional[str] = None,
    project_type: Optional[str] = None,
) -> SkillRating:
    """Record user rating for a skill."""
    
    # Validate stars
    if not 1 <= stars <= 5:
        raise ValueError(f"Stars must be 1-5, got {stars}")
    
    # Generate anonymous user hash
    user_hash = self._get_user_hash()
    
    # Create rating
    rating = SkillRating(
        skill_name=skill,
        user_hash=user_hash,
        stars=stars,
        timestamp=datetime.now(timezone.utc),
        project_type=project_type or "unknown",
        review=review,
        was_helpful=helpful,
        task_succeeded=task_succeeded,
    )
    
    # Store in DB
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("""
            INSERT INTO skill_ratings
            (skill_name, user_hash, stars, timestamp, project_type,
             review, was_helpful, task_succeeded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (...))
        conn.commit()
    
    # Update metrics
    self._update_metrics(skill)
    
    return rating
```

### Recording Usage

```python
def record_usage(
    self,
    skill: str,
    succeeded: bool,
    duration_minutes: Optional[float] = None,
    tokens_saved: Optional[float] = None,
) -> None:
    """Record skill usage for success correlation."""
    
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("""
            INSERT INTO skill_usage
            (skill_name, timestamp, succeeded, duration_minutes, tokens_saved)
            VALUES (?, ?, ?, ?, ?)
        """, (skill, datetime.now(timezone.utc).isoformat(), 
              succeeded, duration_minutes, tokens_saved))
        conn.commit()
    
    # Update metrics to reflect new usage
    self._update_metrics(skill)
```

### Retrieving Ratings

```python
def get_skill_score(self, skill: str) -> Optional[SkillQualityMetrics]:
    """Get aggregated quality metrics for a skill."""
    
    with sqlite3.connect(self.db_path) as conn:
        row = conn.execute("""
            SELECT avg_rating, total_ratings, helpful_percentage,
                   success_correlation, token_efficiency, usage_count,
                   last_updated, stars_5, stars_4, stars_3, stars_2, stars_1
            FROM skill_quality_metrics
            WHERE skill_name = ?
        """, (skill,)).fetchone()
        
        if not row:
            return None
        
        return SkillQualityMetrics(
            skill_name=skill,
            avg_rating=row[0],
            total_ratings=row[1],
            helpful_percentage=row[2],
            success_correlation=row[3],
            token_efficiency=row[4],
            usage_count=row[5],
            last_updated=datetime.fromisoformat(row[6]),
            stars_5=row[7],
            stars_4=row[8],
            stars_3=row[9],
            stars_2=row[10],
            stars_1=row[11],
        )
```

---

## Auto-Prompt System

### SkillRatingPromptManager Class

**Location**: `skill_rating_prompts.py` - `SkillRatingPromptManager`

Intelligent prompt orchestration:

```python
class SkillRatingPromptManager:
    """Detect which skills should prompt for ratings."""
    
    PROMPT_COOLDOWN_HOURS = 24        # Min time between prompts
    RATING_FRESHNESS_DAYS = 14        # Recently rated threshold
    ACTIVATION_LOOKBACK_HOURS = 12    # Usage window
```

### Detecting Due Prompts

```python
def detect_due_prompts(self, limit: int = 3) -> List[RatingPrompt]:
    """Return up to `limit` skills that should be rated."""
    
    # 1. Gather recent usage (last 12 hours)
    usage_map = self._gather_recent_usage()
    
    # 2. Filter by prompt eligibility
    prompts = []
    for skill, info in usage_map.items():
        if self._should_prompt(skill, info):
            prompt = RatingPrompt(
                skill=skill,
                reason=self._build_reason(info),
                last_used=info["last_used"],
                usage_count=info["count"],
                success_rate=info.get("success_rate"),
            )
            prompts.append(prompt)
    
    # 3. Sort by recency, limit results
    prompts.sort(key=lambda p: p.last_used, reverse=True)
    return prompts[:limit]
```

### Prompt Eligibility Logic

```python
def _should_prompt(self, skill: str, usage_info: Dict[str, Any]) -> bool:
    """Determine if skill should prompt for rating."""
    
    # Must have been used
    if usage_info.get("count", 0) == 0:
        return False
    
    # Check cooldown (24 hours since last prompt)
    now = datetime.now(timezone.utc)
    last_prompted = self._get_last_prompted(skill)
    if last_prompted and now - last_prompted < timedelta(hours=24):
        return False  # Too soon
    
    # Check existing rating
    rating = self._get_user_rating(skill)
    if rating:
        # If rated recently (14 days), only prompt if high usage
        if now - rating.timestamp < timedelta(days=14):
            if usage_info.get("count", 0) < 3:
                return False  # Not enough new usage
    
    return True
```

### Gathering Recent Usage

```python
def _gather_recent_usage(self) -> Dict[str, Dict[str, Any]]:
    """Aggregate activation data within lookback window."""
    
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=12)  # 12hr lookback
    usage = {}
    
    # Load activation log
    detailed = self._load_activation_log()
    for activation in detailed:
        skill = activation.get("skill_name")
        ts = parse_timestamp(activation.get("timestamp"))
        
        if not ts or ts < cutoff:
            continue
        
        info = usage.setdefault(skill, {
            "count": 0,
            "last_used": ts,
            "successes": [],
            "task_types": set(),
        })
        
        info["count"] += 1
        if ts > info["last_used"]:
            info["last_used"] = ts
        
        # Track success
        success = activation.get("metrics", {}).get("success")
        if success is not None:
            info["successes"].append(bool(success))
        
        # Track task type
        task_type = activation.get("context", {}).get("task_type")
        if task_type:
            info["task_types"].add(task_type)
    
    # Calculate success rates
    for info in usage.values():
        successes = info.get("successes", [])
        if successes:
            info["success_rate"] = sum(successes) / len(successes)
    
    return usage
```

### Building Prompt Reasons

```python
def _build_reason(self, usage_info: Dict[str, Any]) -> str:
    """Generate human-readable reason for prompt."""
    
    count = usage_info.get("count", 0)
    success_rate = usage_info.get("success_rate")
    task_types = usage_info.get("task_types") or []
    last_used = usage_info.get("last_used")
    
    parts = [f"Used {count} time{'s' if count != 1 else ''} recently"]
    
    if task_types:
        parts.append(f"Tasks: {', '.join(sorted(task_types))}")
    
    if success_rate is not None:
        parts.append(f"Success rate {success_rate * 100:.0f}%")
    
    if isinstance(last_used, datetime):
        elapsed = datetime.now(timezone.utc) - last_used
        hours = max(1, int(elapsed.total_seconds() // 3600))
        parts.append(f"Last used ~{hours}h ago")
    
    return " · ".join(parts)
```

**Example Output**:
```
"Used 3 times recently · Tasks: api-design, code-review · Success rate 67% · Last used ~2h ago"
```

---

## Quality Metrics

### SkillQualityMetrics Model

```python
@dataclass
class SkillQualityMetrics:
    """Automated quality metrics for a skill."""
    
    skill_name: str
    
    # Core metrics
    avg_rating: float              # 0.0-5.0 average
    total_ratings: int             # Number of ratings
    helpful_percentage: float      # % marked helpful
    success_correlation: float     # % tasks succeeded
    token_efficiency: Optional[float]  # Avg tokens saved
    usage_count: int               # Times activated
    
    # Star distribution
    stars_5: int
    stars_4: int
    stars_3: int
    stars_2: int
    stars_1: int
    
    last_updated: datetime
```

### Metric Calculations

**Average Rating**:
```sql
SELECT AVG(stars) as avg_rating
FROM skill_ratings
WHERE skill_name = ?
```

**Helpful Percentage**:
```sql
SELECT 
    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
FROM skill_ratings
WHERE skill_name = ?
```

**Success Correlation**:
```sql
SELECT 
    SUM(CASE WHEN succeeded = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
FROM skill_usage
WHERE skill_name = ?
```

**Star Distribution**:
```sql
SELECT
    SUM(CASE WHEN stars = 5 THEN 1 ELSE 0 END) as stars_5,
    SUM(CASE WHEN stars = 4 THEN 1 ELSE 0 END) as stars_4,
    SUM(CASE WHEN stars = 3 THEN 1 ELSE 0 END) as stars_3,
    SUM(CASE WHEN stars = 2 THEN 1 ELSE 0 END) as stars_2,
    SUM(CASE WHEN stars = 1 THEN 1 ELSE 0 END) as stars_1
FROM skill_ratings
WHERE skill_name = ?
```

### Metrics Update Trigger

```python
def _update_metrics(self, skill: str) -> None:
    """Update aggregated metrics for a skill."""
    
    with sqlite3.connect(self.db_path) as conn:
        # Calculate all metrics in one query
        rating_stats = conn.execute("""
            SELECT
                COUNT(*) as total,
                AVG(stars) as avg_stars,
                SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as helpful_pct,
                SUM(CASE WHEN stars = 5 THEN 1 ELSE 0 END) as stars_5,
                SUM(CASE WHEN stars = 4 THEN 1 ELSE 0 END) as stars_4,
                SUM(CASE WHEN stars = 3 THEN 1 ELSE 0 END) as stars_3,
                SUM(CASE WHEN stars = 2 THEN 1 ELSE 0 END) as stars_2,
                SUM(CASE WHEN stars = 1 THEN 1 ELSE 0 END) as stars_1
            FROM skill_ratings
            WHERE skill_name = ?
        """, (skill,)).fetchone()
        
        usage_stats = conn.execute("""
            SELECT
                COUNT(*) as total_usage,
                SUM(CASE WHEN succeeded = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_pct,
                AVG(tokens_saved) as avg_tokens_saved
            FROM skill_usage
            WHERE skill_name = ?
        """, (skill,)).fetchone()
        
        # Upsert aggregated metrics
        conn.execute("""
            INSERT OR REPLACE INTO skill_quality_metrics
            (skill_name, avg_rating, total_ratings, helpful_percentage,
             success_correlation, token_efficiency, usage_count, last_updated,
             stars_5, stars_4, stars_3, stars_2, stars_1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (...))
        conn.commit()
```

---

## Database Schema

### skill_ratings Table

```sql
CREATE TABLE skill_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    user_hash TEXT NOT NULL,          -- Anonymous SHA256 hash
    stars INTEGER NOT NULL CHECK(stars >= 1 AND stars <= 5),
    timestamp TEXT NOT NULL,          -- ISO 8601 UTC
    project_type TEXT,                -- Optional context
    review TEXT,                      -- Optional review text
    was_helpful BOOLEAN NOT NULL,     -- 0 or 1
    task_succeeded BOOLEAN NOT NULL   -- 0 or 1
);

CREATE INDEX idx_skill_ratings_skill ON skill_ratings(skill_name);
CREATE INDEX idx_skill_ratings_user ON skill_ratings(user_hash, skill_name);
```

### skill_quality_metrics Table

```sql
CREATE TABLE skill_quality_metrics (
    skill_name TEXT PRIMARY KEY,
    avg_rating REAL NOT NULL,
    total_ratings INTEGER NOT NULL,
    helpful_percentage REAL NOT NULL,
    success_correlation REAL NOT NULL,
    token_efficiency REAL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT NOT NULL,
    stars_5 INTEGER NOT NULL DEFAULT 0,
    stars_4 INTEGER NOT NULL DEFAULT 0,
    stars_3 INTEGER NOT NULL DEFAULT 0,
    stars_2 INTEGER NOT NULL DEFAULT 0,
    stars_1 INTEGER NOT NULL DEFAULT 0
);
```

### skill_usage Table

```sql
CREATE TABLE skill_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    succeeded BOOLEAN NOT NULL,
    duration_minutes REAL,
    tokens_saved REAL
);

CREATE INDEX idx_skill_usage_skill ON skill_usage(skill_name);
```

---

## TUI Integration

### Keyboard Shortcut: Ctrl+R

**Location**: Skills view in TUI

**Trigger**:
```python
# In Skills view
async def on_key(self, event: events.Key) -> None:
    if event.key == "ctrl_r":
        await self.show_rating_dialog()
```

### Rating Dialog

```
┌────────────────────────────────────────────────┐
│ Rate Skill: python-testing-patterns            │
├────────────────────────────────────────────────┤
│                                                │
│ How would you rate this skill?                │
│                                                │
│ ⭐ ⭐ ⭐ ⭐ ⭐  (5 stars)                         │
│                                                │
│ Was this skill helpful?                        │
│ ☑ Yes    ☐ No                                 │
│                                                │
│ Did your task succeed?                         │
│ ☑ Yes    ☐ No                                 │
│                                                │
│ Optional review:                               │
│ ┌────────────────────────────────────────┐   │
│ │ Great patterns for test organization   │   │
│ └────────────────────────────────────────┘   │
│                                                │
│ [Submit]  [Cancel]                             │
└────────────────────────────────────────────────┘
```

### Auto-Prompt in TUI

```python
# On TUI startup or view switch
async def on_mount(self) -> None:
    # Check for due prompts
    prompt_mgr = SkillRatingPromptManager()
    prompts = prompt_mgr.detect_due_prompts(limit=1)
    
    if prompts:
        prompt = prompts[0]
        
        # Show non-intrusive notification
        self.notify(
            f"💭 Rate '{prompt.skill}'? {prompt.reason}",
            title="Skill Feedback",
            timeout=10,
        )
        
        # Mark as prompted
        prompt_mgr.mark_prompted(prompt.skill)
```

---

## Analytics & Reports

### Top-Rated Skills

```python
def get_top_rated(
    self, 
    category: Optional[str] = None, 
    limit: int = 10
) -> List[Tuple[str, SkillQualityMetrics]]:
    """Get top-rated skills."""
    
    with sqlite3.connect(self.db_path) as conn:
        rows = conn.execute("""
            SELECT skill_name, avg_rating, total_ratings, helpful_percentage,
                   success_correlation, token_efficiency, usage_count, ...
            FROM skill_quality_metrics
            WHERE total_ratings >= 3  -- Min 3 ratings
            ORDER BY avg_rating DESC, total_ratings DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [(row[0], SkillQualityMetrics(...)) for row in rows]
```

**Example Output**:
```
TOP RATED SKILLS

1. kubernetes-deployment-patterns    ⭐⭐⭐⭐⭐ 4.9/5.0  (12 ratings)
   Success: 94% | Helpful: 100% | Usage: 45

2. python-testing-patterns           ⭐⭐⭐⭐½ 4.6/5.0  (18 ratings)
   Success: 89% | Helpful: 94% | Usage: 67

3. api-design-patterns               ⭐⭐⭐⭐½ 4.5/5.0  (23 ratings)
   Success: 87% | Helpful: 91% | Usage: 89
```

### Recent Reviews

```python
def get_recent_reviews(
    self, 
    skill: str, 
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get recent reviews for a skill."""
    
    with sqlite3.connect(self.db_path) as conn:
        rows = conn.execute("""
            SELECT stars, review, timestamp, was_helpful
            FROM skill_ratings
            WHERE skill_name = ? AND review IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (skill, limit)).fetchall()
        
        reviews = []
        for row in rows:
            ts = datetime.fromisoformat(row[2])
            time_ago = calculate_time_ago(ts)
            
            reviews.append({
                "stars": row[0],
                "review": row[1],
                "timestamp": ts.isoformat(),
                "time_ago": time_ago,  # "2 days ago"
                "was_helpful": row[3],
            })
        
        return reviews
```

### Export Ratings

```python
def export_ratings(
    self, 
    skill: Optional[str] = None
) -> Dict[str, Any]:
    """Export ratings data for analysis."""
    
    # Fetch all ratings (or filter by skill)
    # Fetch all metrics
    
    return {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "ratings": rating_data,      # List of individual ratings
        "metrics": metrics_data,     # List of aggregated metrics
        "total_ratings": len(rating_data),
        "total_skills": len(set(r["skill_name"] for r in rating_data)),
    }
```

---

## Privacy & Anonymity

### Anonymous User Hashing

```python
def _get_user_hash(self) -> str:
    """Generate anonymous user hash."""
    import getpass
    import platform
    
    # Combine machine ID and username
    user_id = f"{platform.node()}-{getpass.getuser()}"
    
    # SHA256 hash
    hash_full = hashlib.sha256(user_id.encode()).hexdigest()
    
    # Truncate to 16 chars
    return hash_full[:16]
    
# Example outputs:
# Machine 1: "a3f8d2e1c4b9f7e6"
# Machine 2: "b7d4f9a2e8c1d6b3"
```

### Privacy Guarantees

✅ **No PII Stored**:
- No usernames
- No email addresses
- No IP addresses
- Only anonymous hash

✅ **Consistent Across Sessions**:
- Same machine + user = same hash
- Enables duplicate detection
- Tracks user's own ratings

✅ **Cannot Reverse**:
- SHA256 is one-way
- Hash truncation adds entropy
- No mapping back to user

---

## CLI Commands

### Rate a Skill

```bash
$ cortex skills rate python-testing-patterns --stars 5 --helpful --succeeded

✅ Recorded rating for python-testing-patterns
   Stars: ⭐⭐⭐⭐⭐
   Helpful: Yes
   Task succeeded: Yes
```

### View Top-Rated

```bash
$ cortex skills top-rated --limit 10

TOP RATED SKILLS (min 3 ratings)

1. kubernetes-deployment-patterns
   ⭐⭐⭐⭐⭐ 4.9/5.0 (12 ratings)
   94% success | 100% helpful | 45 uses

2. python-testing-patterns
   ⭐⭐⭐⭐½ 4.6/5.0 (18 ratings)
   89% success | 94% helpful | 67 uses

3. api-design-patterns
   ⭐⭐⭐⭐½ 4.5/5.0 (23 ratings)
   87% success | 91% helpful | 89 uses
```

### Export Ratings

```bash
$ cortex skills export-ratings --skill python-testing-patterns

✅ Exported ratings to ratings-export.json
   18 ratings
   1 skill
```

---

## Development Guide

### Adding Custom Metrics

**Step 1**: Add column to schema:
```sql
ALTER TABLE skill_quality_metrics
ADD COLUMN custom_metric REAL;
```

**Step 2**: Update metric calculation:
```python
def _update_metrics(self, skill: str) -> None:
    # ... existing metrics
    
    # NEW: Calculate custom metric
    custom_value = conn.execute("""
        SELECT AVG(your_calculation)
        FROM skill_usage
        WHERE skill_name = ?
    """, (skill,)).fetchone()[0]
    
    # Include in upsert
    conn.execute("""
        INSERT OR REPLACE INTO skill_quality_metrics
        (..., custom_metric)
        VALUES (..., ?)
    """, (..., custom_value))
```

**Step 3**: Update data model:
```python
@dataclass
class SkillQualityMetrics:
    # ... existing fields
    custom_metric: Optional[float] = None
```

### Testing Rating System

```python
def test_record_rating(tmp_path):
    """Test rating recording."""
    collector = SkillRatingCollector(home=tmp_path)
    
    rating = collector.record_rating(
        skill="test-skill",
        stars=5,
        helpful=True,
        task_succeeded=True,
        review="Great skill!",
        project_type="python-fastapi",
    )
    
    assert rating.stars == 5
    assert rating.was_helpful
    assert rating.review == "Great skill!"
    
    # Verify in DB
    metrics = collector.get_skill_score("test-skill")
    assert metrics is not None
    assert metrics.avg_rating == 5.0
    assert metrics.total_ratings == 1
```

---

## Related Documentation

- [AI Intelligence System](./AI_INTELLIGENCE_ARCHITECTURE.md)
- [Skill Recommender Integration](./AI_INTELLIGENCE_ARCHITECTURE.md#skill-recommendation-engine)
- [Master Architecture](../../architecture/MASTER_ARCHITECTURE.md)

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-06 | Initial Skill Rating documentation | System Architect |

---

**Document Status**: ✅ Current  
**Maintainer**: Core Team
