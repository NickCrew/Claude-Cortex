# Threat Modeling Tools & Process

## Threat Modeling Tools

### Microsoft Threat Modeling Tool

**Overview:**
- Free Windows desktop application
- Developed by Microsoft Security team
- Integrated STRIDE methodology
- Template-based threat generation

**Features:**
- Visual DFD editor with drag-and-drop
- Automated STRIDE threat generation per element
- Built-in threat knowledge base
- Mitigation recommendations
- Report generation (HTML, PDF)
- Import/export capabilities

**Best Practices:**
```
1. Start with high-level architecture diagram
2. Break down into detailed DFDs (Level 0 → Level 1 → Level 2)
3. Define trust boundaries explicitly (Internet, DMZ, Internal)
4. Let tool generate STRIDE threats automatically
5. Review and customize threats for your context
6. Document mitigations for each threat
7. Export report for security requirements
8. Update model as system evolves
```

**Download:** https://aka.ms/threatmodelingtool

### OWASP Threat Dragon

**Overview:**
- Cross-platform, open source
- Web-based and desktop versions
- Community-driven threat library
- GitHub integration

**Features:**
- DFD modeling with STRIDE analysis
- No vendor lock-in, fully open source
- Web version runs in browser
- Desktop version (Windows, macOS, Linux)
- GitHub repository integration
- Extensible threat templates
- Export to JSON, PDF

**Advantages:**
- Free for all use cases
- Community contributions
- No platform dependencies (web version)
- Privacy-focused (local storage option)
- Active development

**Best For:**
- Open source projects
- Cross-platform teams
- Cloud-native development
- Teams wanting customization

**Website:** https://owasp.org/www-project-threat-dragon/

### IriusRisk

**Overview:**
- Commercial threat modeling platform
- Automated threat library
- DevSecOps integration
- Compliance mapping

**Features:**
- Questionnaire-driven threat modeling
- Automated threat and control suggestions
- SDLC tool integrations (Jira, GitHub, etc.)
- Compliance frameworks (PCI-DSS, ISO 27001, GDPR)
- Risk scoring and prioritization
- Team collaboration features

**Best For:**
- Enterprise environments
- Compliance-heavy industries
- DevSecOps workflows
- Large development teams

### ThreatModeler

**Overview:**
- Collaborative threat modeling platform
- Cloud architecture support
- Real-time collaboration

**Features:**
- Visual threat modeling for cloud (AWS, Azure, GCP)
- Automated threat identification
- Integration with CI/CD pipelines
- Real-time team collaboration
- Compliance reporting
- API for automation

**Best For:**
- Cloud-native applications
- Distributed teams
- Continuous threat modeling

### CAIRIS

**Overview:**
- Requirements and risk management platform
- Persona-based threat modeling
- Open source, research-focused

**Features:**
- Persona and scenario-based modeling
- Requirements traceability
- Risk and vulnerability management
- Security requirements generation
- Attack tree generation
- Export to various formats

**Best For:**
- User-centered security design
- Academic and research projects
- Requirements engineering teams

## Practical Threat Modeling Workflow

### Step-by-Step Process

#### 1. Scope Definition (30 min)

**Objectives:**
- Define what's in scope for threat modeling
- Identify boundaries and assumptions
- List critical assets

**Activities:**
- Identify system components in scope
  - Frontend, backend, databases, APIs, third-party services
- Define trust boundaries
  - Internet/DMZ, DMZ/Internal, User/Admin
- List assets requiring protection
  - User data, financial info, intellectual property, credentials
- Identify compliance requirements
  - PCI-DSS, GDPR, HIPAA, SOC 2, ISO 27001

**Deliverables:**
- Scope document listing components, boundaries, assets
- List of out-of-scope items
- Compliance requirements checklist

#### 2. Architecture Decomposition (1 hour)

**Objectives:**
- Understand how the system works
- Create visual representation
- Document data flows

**Activities:**
- Create data flow diagrams (DFDs)
  - Level 0: Context diagram (high-level)
  - Level 1: Major components and flows
  - Level 2: Detailed subsystem views
- Document external dependencies
  - Third-party APIs, cloud services, CDN
- Identify authentication/authorization points
  - Login, API auth, service-to-service auth
- Map data storage locations
  - Databases, caches, file systems, logs

**Deliverables:**
- Multi-level DFD diagrams
- External dependency list
- Trust boundary map
- Data storage inventory

#### 3. Threat Identification (1-2 hours)

**Objectives:**
- Enumerate potential threats
- Use structured methodologies
- Capture team knowledge

**Activities:**
- Apply STRIDE to each DFD element
  - For each process, data flow, data store
  - Document all applicable STRIDE categories
- Create attack trees for high-value assets
  - Customer data, payment processing, admin access
- Brainstorm threat scenarios with team
  - Include developers, security, operations
  - Consider insider threats, supply chain risks
- Use threat modeling tool for suggestions
  - Leverage built-in threat libraries
  - Customize for your context

**Deliverables:**
- Comprehensive threat list
- Attack tree diagrams
- Threat brainstorming notes
- Tool-generated threat report

#### 4. Risk Assessment (1 hour)

**Objectives:**
- Prioritize threats by risk
- Consider business impact
- Identify quick wins

**Activities:**
- Apply DREAD scoring to each threat
  - Damage, Reproducibility, Exploitability, Affected Users, Discoverability
- Prioritize threats by risk score
  - Critical (7.1-10.0), High (5.1-7.0), Medium (3.1-5.0), Low (0.0-3.0)
- Consider business context and compliance
  - Regulatory requirements, business impact, reputation
- Identify quick wins vs. long-term efforts
  - High impact, low effort = quick wins
  - High impact, high effort = strategic initiatives

**Deliverables:**
- Risk-scored threat list
- Prioritized threat backlog
- Quick win opportunities
- Risk acceptance decisions (if any)

#### 5. Mitigation Planning (1 hour)

**Objectives:**
- Design security controls
- Create actionable requirements
- Assign ownership

**Activities:**
- Design security controls for high-risk threats
  - Preventive, detective, corrective controls
  - Defense in depth approach
- Document mitigation strategies
  - Eliminate, reduce, transfer, accept
- Create security requirements
  - Specific, testable, actionable
- Assign ownership for implementation
  - Development teams, infrastructure, security

**Deliverables:**
- Mitigation strategy document
- Security requirements list (with IDs)
- Ownership assignments
- Implementation timeline

#### 6. Documentation (30 min)

**Objectives:**
- Capture all work
- Enable future updates
- Share with stakeholders

**Activities:**
- Export threat model diagrams
  - DFDs, attack trees, architecture diagrams
- Create security requirements document
  - SEC-### format with acceptance criteria
- Document risk acceptance decisions
  - What risks were accepted and why
- Share with stakeholders
  - Development, security, management, compliance

**Deliverables:**
- Threat model report (PDF/HTML)
- Security requirements document
- Risk acceptance register
- Stakeholder presentation

## Example Security Requirement

**From Threat Model to Actionable Requirement:**

```markdown
## Security Requirement: SEC-001

### Threat Context
- **Threat**: SQL Injection in product search endpoint
- **STRIDE Category**: Tampering, Information Disclosure, Elevation of Privilege
- **Risk Score (DREAD)**: 8.8 (Critical)
  - Damage: 9, Reproducibility: 10, Exploitability: 7, Affected Users: 10, Discoverability: 8
- **Attack Vector**: Attacker submits malicious SQL in search parameter

### Requirement
All database queries MUST use parameterized statements or ORM methods. String concatenation for SQL queries is PROHIBITED.

### Acceptance Criteria
- [ ] No string concatenation in any SQL query
- [ ] ORM (Sequelize) used for all database operations
- [ ] Input validation with allow-list for search terms (alphanumeric, max 100 chars)
- [ ] SQL injection testing included in automated test suite
- [ ] SAST tool (SonarQube) configured to detect SQL concatenation

### Implementation Notes
- **Use Sequelize ORM** for all queries
- For complex raw SQL: `sequelize.query()` with bound parameters
- **Input validation**: `validator.js` for sanitization
- **Test with**: SQLMap, OWASP ZAP, manual injection attempts

### Verification Method
- **Code Review**: Search for raw SQL, string interpolation (`+`, `${}`), `eval()`
- **SAST**: SonarQube rule S2077 (SQL injection detection)
- **DAST**: OWASP ZAP active scan, SQLMap automated testing
- **Manual**: Penetration testing with payloads (`' OR '1'='1`, `'; DROP TABLE--`)

### Owner
- **Team**: Backend Team
- **Primary**: @alice (backend lead)
- **Reviewer**: @bob (security team)
- **Due Date**: Sprint 23 (before v2.0 release)

### Dependencies
- Sequelize ORM already in use ✓
- SonarQube integration (in progress)
- Update test suite with security cases
```

## Best Practices

### Process Integration

**Design Phase:**
- Conduct threat modeling **before** implementation begins
- Include security requirements in design documents
- Review with security team before development starts
- Update architecture diagrams with security annotations

**Development Phase:**
- Implement security controls from threat model
- Document security assumptions in code comments
- Create security test cases (unit, integration, E2E)
- Run SAST/DAST tools as part of CI/CD

**Deployment Phase:**
- Verify security controls in production environment
- Enable monitoring and alerting for identified threats
- Document operational security procedures (runbooks)
- Conduct pre-production security review

**Maintenance Phase:**
- Update threat model when features change
- Re-assess threats periodically (quarterly, annually)
- Track security incidents and update model accordingly
- Review and update mitigations based on new threats

### Team Involvement

**Stakeholders:**

**Developers:**
- Implementation details, code-level threats
- Feasibility of security controls
- Performance impact assessment

**Architects:**
- System design, integration points
- Scalability and availability considerations
- Technology choices and trade-offs

**Security Team:**
- Threat expertise, attack scenarios
- Compliance requirements
- Security control recommendations

**Operations:**
- Deployment architecture, network topology
- Monitoring and incident response
- Operational security procedures

**Product Owners:**
- Business impact and priorities
- Risk acceptance decisions
- Feature vs. security trade-offs

### Common Pitfalls

**Avoid:**

1. **Threat modeling too late**
   - Don't wait until implementation is complete
   - Retrofitting security is expensive and incomplete

2. **Focusing only on external threats**
   - Don't ignore insider threats (malicious or accidental)
   - Consider supply chain and third-party risks

3. **Creating static threat models**
   - Don't let models gather dust
   - Update as system evolves and threats emerge

4. **Over-complicating diagrams**
   - Keep focused on security-relevant flows
   - Too much detail obscures threats

5. **Ignoring low-likelihood, high-impact threats**
   - Nation-state attacks, zero-days
   - Consider business-critical scenarios

6. **Failing to document assumptions**
   - What controls are assumed to exist?
   - What's out of scope and why?

7. **No follow-through**
   - Threats identified but not mitigated
   - Requirements created but not implemented
   - Must track to completion
