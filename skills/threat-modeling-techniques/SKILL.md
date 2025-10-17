---
name: threat-modeling-techniques
description: Threat modeling methodologies using STRIDE, attack trees, and risk assessment for proactive security analysis. Use when designing secure systems, conducting security reviews, or identifying potential attack vectors in applications.
---

# Threat Modeling Techniques

Systematic framework for identifying, analyzing, and mitigating security threats during system design and architecture phases using proven methodologies like STRIDE, attack trees, and risk assessment frameworks.

## When to Use This Skill

- Designing new systems or features with security requirements
- Conducting security architecture reviews
- Identifying attack vectors and threat scenarios
- Assessing security risks before implementation
- Creating security requirements and controls
- Evaluating third-party integrations for security impact
- Planning security testing strategies
- Documenting security design decisions
- Training teams on proactive security thinking
- Supporting security compliance initiatives (SOC 2, ISO 27001)

## Core Threat Modeling Process

**Stages:**
1. **Define** - Understand the system and create architecture diagrams
2. **Identify** - Enumerate threats using structured methodologies
3. **Assess** - Evaluate risk severity and likelihood
4. **Mitigate** - Design controls and countermeasures
5. **Validate** - Review and test security controls

## STRIDE Methodology

**STRIDE** is a threat classification framework developed by Microsoft that categorizes threats into six types.

### Threat Categories

#### S - Spoofing Identity
**Definition:** Pretending to be someone or something else to gain unauthorized access.

**Examples:**
```javascript
// THREAT: Spoofing user identity via JWT manipulation
// Attacker modifies JWT payload without signature verification

// VULNERABLE: No signature verification
app.get('/api/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  const decoded = JSON.parse(Buffer.from(token.split('.')[1], 'base64'));
  // Using decoded.userId without verification
  const user = db.getUser(decoded.userId);
  res.json(user);
});

// MITIGATION: Proper JWT verification
const jwt = require('jsonwebtoken');

app.get('/api/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = db.getUser(decoded.userId);
    res.json(user);
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
});
```

**Mitigations:**
- Strong authentication mechanisms (MFA, certificate-based)
- Digital signatures and cryptographic verification
- Secure credential storage (hashed passwords, encrypted keys)
- Session management with secure tokens
- Mutual TLS for service-to-service communication

#### T - Tampering with Data
**Definition:** Malicious modification of data in transit or at rest.

**Examples:**
```javascript
// THREAT: Man-in-the-middle attack modifying API requests

// VULNERABLE: Unencrypted data transmission
fetch('http://api.example.com/transfer', {
  method: 'POST',
  body: JSON.stringify({ amount: 100, to: 'account123' })
});

// MITIGATION: HTTPS + request signing
const crypto = require('crypto');

function signRequest(data, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(JSON.stringify(data));
  return hmac.digest('hex');
}

const data = { amount: 100, to: 'account123', timestamp: Date.now() };
const signature = signRequest(data, process.env.API_SECRET);

fetch('https://api.example.com/transfer', {
  method: 'POST',
  headers: {
    'X-Signature': signature,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

**Mitigations:**
- TLS/HTTPS for data in transit
- Digital signatures and HMAC for integrity verification
- Input validation and sanitization
- Immutable audit logs
- Database transaction controls and checksums
- File integrity monitoring (FIM)

#### R - Repudiation
**Definition:** Denying actions or transactions without proof otherwise.

**Examples:**
```javascript
// THREAT: User denies performing sensitive action without audit trail

// VULNERABLE: No audit logging
app.post('/api/transfer', authenticate, async (req, res) => {
  await transferFunds(req.user.id, req.body.to, req.body.amount);
  res.json({ success: true });
});

// MITIGATION: Comprehensive audit logging
const winston = require('winston');
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'audit.log' })
  ]
});

app.post('/api/transfer', authenticate, async (req, res) => {
  const auditEvent = {
    action: 'FUND_TRANSFER',
    userId: req.user.id,
    from: req.user.accountId,
    to: req.body.to,
    amount: req.body.amount,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date().toISOString(),
    sessionId: req.session.id
  };

  logger.info('Fund transfer initiated', auditEvent);

  try {
    const result = await transferFunds(req.user.id, req.body.to, req.body.amount);
    logger.info('Fund transfer completed', { ...auditEvent, transactionId: result.id });
    res.json({ success: true, transactionId: result.id });
  } catch (err) {
    logger.error('Fund transfer failed', { ...auditEvent, error: err.message });
    res.status(500).json({ error: 'Transfer failed' });
  }
});
```

**Mitigations:**
- Comprehensive audit logging (who, what, when, where)
- Digital signatures for non-repudiation
- Tamper-proof log storage (append-only, immutable)
- Secure time-stamping services
- Multi-party transaction approval workflows
- Legal agreements and terms of service

#### I - Information Disclosure
**Definition:** Exposing information to unauthorized individuals.

**Examples:**
```javascript
// THREAT: Exposing sensitive data through verbose error messages

// VULNERABLE: Stack traces exposed to users
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    sql: err.sql // Exposes database structure
  });
});

// MITIGATION: Generic errors, detailed internal logs
app.use((err, req, res, next) => {
  // Log internally with full details
  logger.error('Request error', {
    error: err.message,
    stack: err.stack,
    sql: err.sql,
    requestId: req.id,
    userId: req.user?.id
  });

  // Return generic error to client
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id
  });
});
```

**Mitigations:**
- Encryption at rest and in transit (AES-256, TLS 1.3)
- Access control enforcement (RBAC, ABAC)
- Data classification and handling policies
- Secure key management (KMS, HSM)
- Data masking and tokenization
- Generic error messages to users
- Security headers (prevent MIME sniffing, clickjacking)

#### D - Denial of Service
**Definition:** Making systems unavailable to legitimate users.

**Examples:**
```javascript
// THREAT: Resource exhaustion through unbounded operations

// VULNERABLE: No rate limiting or resource constraints
app.post('/api/search', async (req, res) => {
  const results = await db.query(`SELECT * FROM products WHERE name LIKE '%${req.body.query}%'`);
  res.json(results); // Returns unlimited rows
});

// MITIGATION: Rate limiting + pagination + timeouts
const rateLimit = require('express-rate-limit');

const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 20 // 20 requests per minute
});

app.post('/api/search', searchLimiter, async (req, res) => {
  const query = req.body.query;
  const page = parseInt(req.body.page) || 1;
  const limit = Math.min(parseInt(req.body.limit) || 10, 100); // Max 100 items
  const offset = (page - 1) * limit;

  // Use parameterized query with LIMIT
  const results = await db.query(
    'SELECT * FROM products WHERE name LIKE ? LIMIT ? OFFSET ?',
    [`%${query}%`, limit, offset],
    { timeout: 5000 } // 5 second query timeout
  );

  res.json({
    results,
    page,
    limit,
    hasMore: results.length === limit
  });
});
```

**Mitigations:**
- Rate limiting and throttling
- Resource quotas and timeouts
- Input validation (size limits, complexity limits)
- Load balancing and auto-scaling
- CDN and caching strategies
- Anti-automation measures (CAPTCHA)
- DDoS protection services (Cloudflare, AWS Shield)

#### E - Elevation of Privilege
**Definition:** Gaining capabilities without proper authorization.

**Examples:**
```javascript
// THREAT: Privilege escalation through parameter manipulation

// VULNERABLE: Client-controlled role assignment
app.post('/api/users', authenticate, async (req, res) => {
  const user = await db.createUser({
    username: req.body.username,
    password: req.body.password,
    role: req.body.role // Attacker sets role: 'admin'
  });
  res.json(user);
});

// MITIGATION: Server-side role enforcement
app.post('/api/users', authenticate, requireRole('admin'), async (req, res) => {
  // Only admins can create users
  // Default role assigned by system, not client
  const user = await db.createUser({
    username: req.body.username,
    password: req.body.password,
    role: 'user', // Always default to least privilege
    createdBy: req.user.id
  });

  logger.info('User created', {
    newUserId: user.id,
    createdBy: req.user.id,
    timestamp: new Date()
  });

  res.json(user);
});

// Separate endpoint for role changes with strict controls
app.patch('/api/users/:id/role', authenticate, requireRole('admin'), async (req, res) => {
  const targetUser = await db.getUser(req.params.id);

  // Prevent self-elevation
  if (targetUser.id === req.user.id) {
    return res.status(403).json({ error: 'Cannot modify own role' });
  }

  // Validate role value
  const validRoles = ['user', 'moderator', 'admin'];
  if (!validRoles.includes(req.body.role)) {
    return res.status(400).json({ error: 'Invalid role' });
  }

  await db.updateUser(req.params.id, { role: req.body.role });

  logger.warn('Role changed', {
    targetUserId: targetUser.id,
    oldRole: targetUser.role,
    newRole: req.body.role,
    changedBy: req.user.id,
    timestamp: new Date()
  });

  res.json({ success: true });
});
```

**Mitigations:**
- Principle of least privilege
- Role-based access control (RBAC)
- Input validation on privilege-related parameters
- Separation of duties
- Privilege use logging and monitoring
- Secure defaults (deny by default)
- Regular privilege audits

## Attack Trees

**Definition:** Hierarchical diagrams showing attack paths from goals to methods.

### Structure
```
[Root: Attack Goal]
    |
    +-- [OR] Method 1
    |       |
    |       +-- [AND] Step 1.1
    |       +-- [AND] Step 1.2
    |
    +-- [OR] Method 2
            |
            +-- [AND] Step 2.1
```

### Example: Unauthorized Data Access

```
[Goal: Access Customer Database]
    |
    +-- [OR] Exploit SQL Injection
    |       |
    |       +-- [AND] Find vulnerable input field
    |       +-- [AND] Craft malicious SQL payload
    |       +-- [AND] Extract data from database
    |
    +-- [OR] Steal Admin Credentials
    |       |
    |       +-- [AND] Phishing attack on admin
    |       +-- [AND] Bypass 2FA (if enabled)
    |       +-- [AND] Login with stolen credentials
    |
    +-- [OR] Exploit Misconfigured Access Controls
            |
            +-- [AND] Enumerate API endpoints
            +-- [AND] Find unprotected endpoint
            +-- [AND] Access data without authentication
```

### Creating Attack Trees

**Process:**
1. Define the attacker's goal (root node)
2. Identify alternative attack methods (OR nodes)
3. Break down each method into required steps (AND nodes)
4. Assign attributes (cost, skill, detection likelihood)
5. Analyze most likely attack paths
6. Prioritize mitigations for high-risk paths

**Attributes to Track:**
- **Cost**: Resources required by attacker (low/medium/high)
- **Skill Level**: Technical expertise needed (novice/intermediate/expert)
- **Detection**: Likelihood of being detected (low/medium/high)
- **Impact**: Damage if successful (low/medium/high/critical)

## Data Flow Diagrams (DFD)

**Purpose:** Visualize how data moves through the system to identify threat points.

### DFD Elements

**Key Components:**
- **External Entity** (rectangle): Users, external systems
- **Process** (circle): Application components, services
- **Data Store** (parallel lines): Databases, file systems, caches
- **Data Flow** (arrow): Data movement between elements
- **Trust Boundary** (dashed line): Security context changes

### Example DFD

```
[User Browser] ---(1) HTTPS Request---> [Web Server]
                                              |
                                         (2) Query
                                              |
                                              v
                                      [Application Server]
                                              |
                                         (3) SQL
                                              |
                                              v
                                         [Database]
                                              |
                                         (4) Logs
                                              |
                                              v
                                      [Audit Log Store]

Trust Boundaries:
- Between User Browser and Web Server (Internet)
- Between Web Server and Application Server (DMZ)
- Between Application Server and Database (Internal Network)
```

### Threat Analysis per DFD Element

**For each data flow, consider STRIDE:**

1. **User → Web Server (HTTPS)**
   - **S**: Spoofing via stolen credentials
   - **T**: Tampering if HTTPS not enforced
   - **R**: User denies sending request
   - **I**: Sniffing credentials over network
   - **D**: DDoS attack on web server
   - **E**: Session hijacking

2. **Application → Database (SQL)**
   - **S**: Spoofing database credentials
   - **T**: SQL injection modifying queries
   - **R**: No audit of database changes
   - **I**: Unauthorized data access
   - **D**: Resource exhaustion
   - **E**: Privilege escalation via SQL injection

## Trust Boundaries

**Definition:** Lines separating different trust levels in a system.

### Common Trust Boundaries

1. **Network Boundaries**
   - Internet → DMZ
   - DMZ → Internal Network
   - Internal → Secure Enclave

2. **Process Boundaries**
   - User Mode → Kernel Mode
   - Guest VM → Host System
   - Container → Host

3. **User Boundaries**
   - Anonymous → Authenticated
   - User → Administrator
   - Internal → External Users

### Analyzing Trust Boundaries

**Questions to Ask:**
- What authentication is required to cross the boundary?
- What authorization checks are performed?
- Is data encrypted when crossing the boundary?
- Are all inputs validated when crossing the boundary?
- Is the boundary logged and monitored?

## Risk Assessment with DREAD

**DREAD** is a risk assessment framework for quantifying threat severity.

### DREAD Criteria

Each criterion scored 0-10, average = risk score

#### D - Damage Potential
**Question:** How much damage if exploited?
- 0 = No damage
- 5 = Information disclosure
- 10 = Complete system compromise

#### R - Reproducibility
**Question:** How easy to reproduce?
- 0 = Very difficult
- 5 = Authenticated user required
- 10 = Anyone can reproduce easily

#### E - Exploitability
**Question:** How easy to exploit?
- 0 = Advanced skills and custom tools
- 5 = Moderate skill, available tools
- 10 = Web browser or scripting only

#### A - Affected Users
**Question:** How many users affected?
- 0 = Single user
- 5 = Some users or subset
- 10 = All users or critical data

#### D - Discoverability
**Question:** How easy to discover?
- 0 = Very hard to find
- 5 = Found with moderate effort
- 10 = Obvious or public knowledge

### DREAD Example

**Threat:** SQL Injection in login form

- **Damage**: 9 (Database compromise, data theft)
- **Reproducibility**: 10 (Easy to reproduce)
- **Exploitability**: 7 (Moderate skill, tools available)
- **Affected Users**: 10 (All users, entire database)
- **Discoverability**: 8 (Common vulnerability, easy to test)

**Risk Score:** (9 + 10 + 7 + 10 + 8) / 5 = **8.8 (CRITICAL)**

## Mitigation Strategies

### Prioritization Matrix

**Risk Level = Likelihood × Impact**

| Impact →     | Low (1) | Medium (2) | High (3) | Critical (4) |
|--------------|---------|------------|----------|--------------|
| **High (3)** | Medium  | High       | Critical | Critical     |
| **Med (2)**  | Low     | Medium     | High     | Critical     |
| **Low (1)**  | Low     | Low        | Medium   | High         |

### Mitigation Approaches

**1. Eliminate**
- Remove vulnerable feature entirely
- Disable unnecessary functionality
- Reduce attack surface

**2. Reduce**
- Implement security controls
- Add authentication/authorization
- Apply principle of least privilege

**3. Transfer**
- Use third-party security services
- Implement insurance policies
- Share risk with cloud provider

**4. Accept**
- Document risk acceptance
- Implement monitoring and detection
- Plan incident response

### Control Types

**Preventive:** Stop threats before they occur
- Input validation
- Access controls
- Encryption

**Detective:** Identify threats in progress
- Logging and monitoring
- Intrusion detection systems (IDS)
- Security information and event management (SIEM)

**Corrective:** Respond to detected threats
- Incident response procedures
- Backup and recovery
- Patching and updates

## Threat Modeling Tools

### Microsoft Threat Modeling Tool

**Features:**
- Visual DFD editor
- Automated STRIDE threat generation
- Threat templates and knowledge base
- Mitigation recommendations
- Report generation

**Best Practices:**
```
1. Start with high-level architecture
2. Break down into detailed DFDs
3. Define trust boundaries explicitly
4. Let tool generate STRIDE threats
5. Review and customize threats
6. Document mitigations
7. Export for security requirements
```

### OWASP Threat Dragon

**Features:**
- Cross-platform, open source
- DFD modeling
- STRIDE threat identification
- Web-based and desktop versions
- GitHub integration

**Advantages:**
- No vendor lock-in
- Community-driven threat library
- Extensible and customizable
- Free for all use cases

### Other Tools

**IriusRisk**
- Automated threat modeling
- Integration with SDLC tools
- Compliance mapping

**ThreatModeler**
- Collaborative threat modeling
- DevSecOps integration
- Cloud architecture support

**CAIRIS**
- Requirements and risk management
- Persona-based threat modeling
- Security requirements generation

## Threat Modeling Best Practices

### Process Integration

**Design Phase:**
- Conduct threat modeling before implementation
- Include security requirements in design documents
- Review with security team

**Development Phase:**
- Implement security controls from threat model
- Document security assumptions
- Create security test cases

**Deployment Phase:**
- Verify security controls in production
- Enable monitoring for identified threats
- Document operational security procedures

**Maintenance Phase:**
- Update threat model when features change
- Re-assess threats periodically
- Track security incidents and update model

### Team Involvement

**Stakeholders:**
- **Developers**: Implementation details, code-level threats
- **Architects**: System design, integration points
- **Security Team**: Threat expertise, attack scenarios
- **Operations**: Deployment, monitoring, incident response
- **Product Owners**: Business impact, risk acceptance decisions

### Common Pitfalls

**Avoid:**
- Threat modeling too late (after implementation)
- Focusing only on external threats (ignore insider threats)
- Creating threat models that gather dust (no updates)
- Over-complicating diagrams (keep focused)
- Ignoring low-likelihood, high-impact threats
- Failing to document assumptions and decisions

## Practical Workflow

### Step-by-Step Process

**1. Scope Definition (30 min)**
- Identify system components in scope
- Define trust boundaries
- List assets requiring protection
- Identify compliance requirements

**2. Architecture Decomposition (1 hour)**
- Create data flow diagrams
- Document external dependencies
- Identify authentication/authorization points
- Map data storage locations

**3. Threat Identification (1-2 hours)**
- Apply STRIDE to each DFD element
- Create attack trees for high-value assets
- Brainstorm threat scenarios with team
- Use threat modeling tool for suggestions

**4. Risk Assessment (1 hour)**
- Apply DREAD scoring to each threat
- Prioritize threats by risk score
- Consider business context and compliance
- Identify quick wins vs. long-term efforts

**5. Mitigation Planning (1 hour)**
- Design security controls for high-risk threats
- Document mitigation strategies
- Create security requirements
- Assign ownership for implementation

**6. Documentation (30 min)**
- Export threat model diagrams
- Create security requirements document
- Document risk acceptance decisions
- Share with stakeholders

### Example Security Requirement

**From Threat Model:**
```
Threat: SQL Injection in search endpoint
Risk Score: 8.8 (Critical)

Security Requirement:
- ID: SEC-001
- Component: Search API
- Requirement: All database queries MUST use parameterized statements
- Acceptance Criteria:
  * No string concatenation in SQL queries
  * ORM or prepared statements used exclusively
  * Input validation with allow-list for search terms
  * SQL injection testing included in test suite
- Owner: Backend Team
- Due Date: Sprint 23
- Verification: Code review + SAST + manual testing
```

## Resources

- **Microsoft Threat Modeling Tool**: https://aka.ms/threatmodelingtool
- **OWASP Threat Dragon**: https://owasp.org/www-project-threat-dragon/
- **STRIDE Documentation**: https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **Attack Tree Framework**: https://www.schneier.com/academic/archives/1999/12/attack_trees.html
- **NIST Threat Modeling**: https://csrc.nist.gov/projects/threat-modeling
- **PASTA Methodology**: Process for Attack Simulation and Threat Analysis
- **LINDDUN**: Privacy threat modeling framework
- **OCTAVE**: Operationally Critical Threat, Asset, and Vulnerability Evaluation
- **Threat Modeling Manifesto**: https://www.threatmodelingmanifesto.org/
