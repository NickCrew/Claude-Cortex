# DREAD Risk Assessment

**DREAD** is a risk assessment framework for quantifying threat severity.

## DREAD Criteria

Each criterion scored **0-10**, average = risk score

### D - Damage Potential

**Question:** How much damage if exploited?

**Scoring:**
- **0-2**: Minimal impact, cosmetic issues
- **3-4**: Limited data exposure, temporary service degradation
- **5-6**: Significant data exposure, extended downtime
- **7-8**: Major breach, customer data compromised
- **9-10**: Complete system compromise, catastrophic damage

**Examples:**
- **2**: Display bug in UI
- **5**: Exposure of non-sensitive user data
- **9**: Full database compromise with PII/financial data

### R - Reproducibility

**Question:** How easy to reproduce the attack?

**Scoring:**
- **0-2**: Very difficult, requires specific conditions
- **3-4**: Difficult, requires timing or race conditions
- **5-6**: Moderate, requires authenticated access
- **7-8**: Easy, any authenticated user can reproduce
- **9-10**: Trivial, anyone can reproduce easily

**Examples:**
- **2**: Requires specific hardware and network conditions
- **5**: Requires valid user account and specific request timing
- **10**: Works every time with simple HTTP request

### E - Exploitability

**Question:** How easy to exploit?

**Scoring:**
- **0-2**: Requires expert skills and custom tools
- **3-4**: Requires advanced knowledge and tool modification
- **5-6**: Requires moderate skill and available tools
- **7-8**: Requires basic scripting knowledge
- **9-10**: Web browser or curl command only

**Examples:**
- **2**: Requires reverse engineering and custom exploit development
- **5**: Use Burp Suite with some configuration
- **10**: Copy-paste command from blog post

### A - Affected Users

**Question:** How many users affected?

**Scoring:**
- **0-2**: Single user or small subset
- **3-4**: Specific user group or feature subset
- **5-6**: Significant portion of users
- **7-8**: Majority of users or critical subset
- **9-10**: All users, entire system, or critical data

**Examples:**
- **2**: Single admin account
- **5**: All users of premium feature (20% of user base)
- **10**: Entire customer database exposed

### D - Discoverability

**Question:** How easy to discover the vulnerability?

**Scoring:**
- **0-2**: Very hard to find, requires source code access
- **3-4**: Requires detailed analysis and fuzzing
- **5-6**: Found with moderate effort and scanning
- **7-8**: Found with automated scanners
- **9-10**: Obvious, visible in URL or public documentation

**Examples:**
- **2**: Logic flaw requiring deep code analysis
- **5**: Found by targeted security testing
- **10**: SQL injection in URL parameter, found by SQLMap

## DREAD Scoring Examples

### Example 1: SQL Injection in Login Form

**Threat:** SQL Injection in publicly accessible login endpoint

**Scoring:**
- **Damage**: 9 (Full database compromise, data theft)
- **Reproducibility**: 10 (Easy to reproduce every time)
- **Exploitability**: 7 (Moderate skill, tools available like SQLMap)
- **Affected Users**: 10 (All users, entire database at risk)
- **Discoverability**: 8 (Common vulnerability, automated scanners find it)

**Risk Score:** (9 + 10 + 7 + 10 + 8) / 5 = **8.8 (CRITICAL)**

**Priority:** Immediate fix required

### Example 2: Missing Rate Limiting on API

**Threat:** No rate limiting on password reset endpoint

**Scoring:**
- **Damage**: 6 (Account takeover possible via brute force)
- **Reproducibility**: 10 (Easy to reproduce)
- **Exploitability**: 8 (Simple scripting required)
- **Affected Users**: 7 (All users vulnerable, but requires targeting)
- **Discoverability**: 6 (Found with moderate testing)

**Risk Score:** (6 + 10 + 8 + 7 + 6) / 5 = **7.4 (HIGH)**

**Priority:** Fix in next sprint

### Example 3: Information Disclosure in Comments

**Threat:** HTML comments contain internal IP addresses

**Scoring:**
- **Damage**: 3 (Minor information disclosure, aids reconnaissance)
- **Reproducibility**: 10 (Always present in source)
- **Exploitability**: 10 (View source in any browser)
- **Affected Users**: 2 (Information disclosure, not direct user impact)
- **Discoverability**: 10 (Obvious in HTML source)

**Risk Score:** (3 + 10 + 10 + 2 + 10) / 5 = **7.0 (MEDIUM-HIGH)**

**Priority:** Fix soon, but not critical

### Example 4: XSS in Admin-Only Field

**Threat:** Stored XSS in admin panel description field

**Scoring:**
- **Damage**: 7 (Admin session hijacking, high privileges)
- **Reproducibility**: 10 (Easy to reproduce)
- **Exploitability**: 8 (Simple XSS payload)
- **Affected Users**: 2 (Only affects admins who view the field)
- **Discoverability**: 4 (Requires admin access to discover)

**Risk Score:** (7 + 10 + 8 + 2 + 4) / 5 = **6.2 (MEDIUM)**

**Priority:** Fix in backlog, but monitor for abuse

## Risk Level Interpretation

**Risk Score Ranges:**
- **0.0 - 3.0**: Low - Monitor, fix when convenient
- **3.1 - 5.0**: Medium - Fix in upcoming releases
- **5.1 - 7.0**: High - Prioritize for next sprint
- **7.1 - 10.0**: Critical - Immediate action required

## DREAD Worksheet Template

```markdown
## Threat: [Threat Name]

### DREAD Scoring

**D - Damage Potential**: [0-10]
- Justification: [Explain the potential damage]

**R - Reproducibility**: [0-10]
- Justification: [Explain how easily it can be reproduced]

**E - Exploitability**: [0-10]
- Justification: [Explain the required skill and tools]

**A - Affected Users**: [0-10]
- Justification: [Explain the scope of impact]

**D - Discoverability**: [0-10]
- Justification: [Explain how easily it can be found]

### Risk Calculation

**Risk Score**: ([D] + [R] + [E] + [A] + [D]) / 5 = **[Score]**

**Risk Level**: [Low/Medium/High/Critical]

**Priority**: [When to fix]

### Recommended Actions

- [List mitigations]
```

## Limitations of DREAD

### Known Issues

- **Subjectivity**: Scores can vary between assessors
- **Binary thinking**: Doesn't capture nuanced risks well
- **Evolving threats**: Scores may change as exploits become easier
- **Context dependency**: Same vulnerability, different risk in different systems

### Improvements

- **Calibration sessions**: Team agreement on scoring examples
- **Regular updates**: Re-assess as threat landscape changes
- **Combine with other methods**: Use with STRIDE, attack trees
- **Document assumptions**: Why you scored each criterion
