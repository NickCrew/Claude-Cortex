# Research Methods

Reference for planning and executing user research across qualitative, quantitative, and synthesis methods.

## Interview Techniques

### Contextual Inquiry

Observe and interview users in their actual work environment.

**When to use**: Discovery phase, understanding real workflows, uncovering workarounds.

**Protocol**:
1. Schedule a session in the user's environment (remote screen-share counts)
2. Ask the user to perform their normal tasks while narrating
3. Observe first, then ask clarifying questions
4. Focus on what they do, not what they say they do
5. Note workarounds, tool-switching, and emotional reactions

**Key questions**:
- "Walk me through how you normally do this."
- "I noticed you did X there -- can you tell me why?"
- "What would make this easier?"

### Structured Interviews

Consistent question set across all participants for comparability.

**Template**:
```
1. Warm-up: Role, experience, context (2-3 min)
2. Core questions: 5-8 open-ended questions tied to research goals
3. Probes: Follow-up prompts for depth ("Tell me more about...", "Why?")
4. Wrap-up: Anything we missed, next steps (2 min)
```

**Best practices**:
- Write questions in advance and test with a pilot participant
- Ask open-ended questions first, then narrow
- Avoid leading questions ("Don't you think X is hard?")
- Record with consent; take notes as backup

### Unstructured Interviews

Conversational format guided by themes rather than fixed questions.

**When to use**: Early discovery, exploring unknown problem spaces, building rapport.

**Approach**:
- Prepare 3-5 topic areas, not specific questions
- Follow the participant's lead
- Use silence to encourage elaboration
- Redirect gently if the conversation drifts too far

### Diary Studies

Participants self-report over days or weeks.

**Setup**:
1. Define the behavior or experience to capture
2. Choose capture method (form, app, text message, email)
3. Set frequency (event-triggered or time-triggered)
4. Run for 1-4 weeks depending on behavior cadence
5. Follow up with interviews to clarify entries

**Prompt template**:
```
When [trigger event] happens, record:
- What were you trying to do?
- What happened?
- How did it make you feel?
- What did you do next?
```

## Survey Design Patterns

### Question Types

| Type | Use For | Example |
| --- | --- | --- |
| **Likert scale** | Attitudes, satisfaction | "Rate your satisfaction: 1-5" |
| **Multiple choice** | Categorization, preferences | "Which feature do you use most?" |
| **Open-ended** | Discovery, qualitative depth | "Describe your biggest frustration" |
| **Ranking** | Prioritization | "Rank these features by importance" |
| **Task success** | Usability measurement | "Were you able to complete X? Yes/No" |

### Bias Avoidance Checklist

- [ ] No leading questions ("How much did you enjoy...?")
- [ ] No double-barreled questions ("Is it fast and reliable?")
- [ ] Response options are exhaustive and mutually exclusive
- [ ] Neutral option available for opinion questions
- [ ] Question order does not prime later answers
- [ ] No jargon or ambiguous terms
- [ ] Pilot tested with 3-5 people before launch

### Sampling Guidelines

| Method | When | Trade-off |
| --- | --- | --- |
| **Random** | Generalizable quantitative findings | Requires large participant pool |
| **Stratified** | Need representation across segments | More recruitment effort |
| **Convenience** | Quick directional signal | Results may not generalize |
| **Purposive** | Specific user type or behavior | Small sample, deep insight |

**Minimum sample sizes**:
- Usability testing: 5-8 per user segment
- Surveys (quantitative): 30+ for statistical patterns, 100+ for segmentation
- Interviews (qualitative): 8-12 for thematic saturation

## Usability Testing Protocols

### Task-Based Testing

Assign specific tasks and measure success, time, and errors.

**Session template**:
```
1. Introduction and consent (3 min)
2. Background questions (2 min)
3. Task scenarios (3-5 tasks, 5-8 min each):
   - Read task aloud
   - Observe without helping
   - Note: success/failure, time, errors, path taken
4. Post-task questionnaire (SUS, SEQ, or custom)
5. Debrief and open questions (5 min)
```

**Writing good tasks**:
- Frame as realistic scenarios, not instructions
- Good: "You want to invite a teammate to your project. Do that now."
- Bad: "Click the Settings button and add a user."

### Think-Aloud Protocol

Participants verbalize their thought process while performing tasks.

**Moderator prompts**:
- "Keep talking -- what are you thinking?"
- "What are you looking for right now?"
- "What do you expect to happen?"

**When to use**: Understanding mental models, identifying confusion points, evaluating information architecture.

**Caution**: Think-aloud adds cognitive load. Use concurrent think-aloud for simple tasks, retrospective think-aloud for complex ones.

### A/B Testing

Compare two variants with real traffic to measure behavioral differences.

**Planning checklist**:
- [ ] Single variable isolated between variants
- [ ] Primary metric defined (conversion, time-on-task, error rate)
- [ ] Sample size calculated for statistical power
- [ ] Test duration accounts for weekly cycles (minimum 1-2 weeks)
- [ ] Segmentation plan defined (new vs returning, device, etc.)
- [ ] Guardrail metrics set (metrics that must not regress)

## Synthesis Patterns

### Affinity Mapping

Group observations into themes to find patterns.

**Process**:
1. Write one observation per sticky note (physical or digital)
2. Spread all notes visibly
3. Silently group related notes (no labels yet)
4. Name each group after a theme emerges
5. Look for super-groups and outliers
6. Document themes with supporting evidence counts

**Tips**:
- Use verbatim quotes, not interpretations, on the notes
- 50-200 notes is a productive range
- Involve 2-3 team members for diverse grouping perspectives

### Journey Mapping from Research

Translate research findings into a journey map.

**Steps**:
1. List all stages the user moves through (from interview/observation data)
2. For each stage, map: actions, touchpoints, emotions, pain points
3. Mark emotional highs and lows with evidence (quotes, metrics)
4. Identify moments of truth (where users decide to continue or abandon)
5. Annotate opportunities aligned to pain points

### Persona Creation

Build personas grounded in research data, not assumptions.

**Persona template**:
```
## [Name] - [Role/Archetype]

**Demographics**: [Relevant context only]
**Goals**: What they are trying to achieve
**Frustrations**: Recurring pain points from research
**Behaviors**: Observed patterns (tools used, frequency, workarounds)
**Quote**: Representative verbatim quote from interviews
**Scenario**: A day-in-the-life narrative grounded in observations
```

**Validation rule**: Every persona attribute must trace back to at least 2 research participants.

## Evidence Triangulation

Strengthen findings by confirming them across multiple sources.

### Triangulation Matrix

| Finding | Interview Evidence | Survey Data | Behavioral/Analytics | Confidence |
| --- | --- | --- | --- | --- |
| Users struggle with X | 6/10 mentioned it | 72% rated it hard | 45% drop-off at step | High |
| Users want feature Y | 3/10 requested it | Not asked | No signal | Low |

### Confidence Levels

- **High**: Confirmed by 3+ methods or 2 methods with strong signal
- **Medium**: Confirmed by 2 methods or 1 method with strong quantitative signal
- **Low**: Single method or anecdotal; needs further validation

### Resolving Contradictions

When sources disagree:
1. Check for different user segments producing different signals
2. Distinguish between what users say (interviews) vs what they do (analytics)
3. Look at recency -- newer data may reflect changed behavior
4. Run a targeted follow-up study to break the tie

## Research Planning Templates

### Research Brief

```
## Research Brief: [Study Name]

**Research question**: What do we need to learn?
**Business context**: Why does this matter now?
**Method**: [Interview / Survey / Usability test / etc.]
**Participants**: [Segment, count, recruitment source]
**Timeline**: [Recruitment → Sessions → Analysis → Report]
**Deliverables**: [Report, personas, journey map, recommendations]
**Stakeholders**: [Who needs the findings]
```

### Session Planning Checklist

- [ ] Research questions defined and prioritized
- [ ] Method selected and protocol drafted
- [ ] Participant criteria documented
- [ ] Recruitment plan in place
- [ ] Consent form / recording permissions prepared
- [ ] Discussion guide or task list pilot-tested
- [ ] Note-taking template ready
- [ ] Observer roles assigned (moderator, note-taker, time-keeper)
- [ ] Synthesis session scheduled within 48 hours of last session

### Reporting Template

```
## Research Report: [Study Name]

### Executive Summary
Key findings in 3-5 bullets.

### Method
Who, how, when, sample size.

### Findings
Organized by theme, each with:
- Observation
- Supporting evidence (quotes, data)
- Confidence level

### Recommendations
Prioritized actions tied to findings.

### Appendix
Raw data references, participant demographics, full question guide.
```
