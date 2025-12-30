# Data Flow Diagrams (DFD)

**Purpose:** Visualize how data moves through the system to identify threat points.

## DFD Elements

### Key Components

**External Entity** (rectangle)
- Users, external systems, third-party services
- Outside the system boundary
- Sources or destinations of data

**Process** (circle)
- Application components, services, functions
- Transform or process data
- Trust boundaries often cross between processes

**Data Store** (parallel lines)
- Databases, file systems, caches, message queues
- Persistent or temporary storage
- Potential targets for information disclosure

**Data Flow** (arrow)
- Data movement between elements
- Can cross trust boundaries
- Each flow is a potential attack vector

**Trust Boundary** (dashed line)
- Security context changes
- Authentication/authorization required
- Critical points for STRIDE analysis

## Example DFD

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

## Threat Analysis per DFD Element

### For Each Data Flow, Consider STRIDE

#### Flow 1: User → Web Server (HTTPS)

**Spoofing**
- Stolen credentials, session hijacking
- Mitigation: Strong authentication, MFA, session expiration

**Tampering**
- Man-in-the-middle if HTTPS not enforced
- Mitigation: Force HTTPS, HSTS header, certificate pinning

**Repudiation**
- User denies sending request
- Mitigation: Audit logging with request signatures

**Information Disclosure**
- Sniffing credentials over network
- Mitigation: TLS 1.3, encrypted connections

**Denial of Service**
- DDoS attack on web server
- Mitigation: Rate limiting, WAF, DDoS protection

**Elevation of Privilege**
- Session hijacking, cookie theft
- Mitigation: HttpOnly/Secure cookies, CSRF tokens

#### Flow 2: Application → Database (SQL)

**Spoofing**
- Spoofing database credentials
- Mitigation: Connection pooling, credential rotation, least privilege

**Tampering**
- SQL injection modifying queries
- Mitigation: Parameterized queries, ORM, input validation

**Repudiation**
- No audit of database changes
- Mitigation: Database audit logs, transaction logging

**Information Disclosure**
- Unauthorized data access, SQL injection
- Mitigation: Access controls, encryption at rest, query filtering

**Denial of Service**
- Resource exhaustion, slow queries
- Mitigation: Query timeouts, connection limits, query optimization

**Elevation of Privilege**
- Privilege escalation via SQL injection
- Mitigation: Least privilege DB accounts, parameterized queries

## Trust Boundaries

### Definition
Lines separating different trust levels in a system.

### Common Trust Boundaries

#### 1. Network Boundaries
- **Internet → DMZ**: Public to semi-public
- **DMZ → Internal Network**: Semi-public to private
- **Internal → Secure Enclave**: Private to highly restricted

**Security Controls:**
- Firewalls, network segmentation
- IDS/IPS systems
- VPN/private connections

#### 2. Process Boundaries
- **User Mode → Kernel Mode**: Application to OS
- **Guest VM → Host System**: Virtual to physical
- **Container → Host**: Isolated to privileged

**Security Controls:**
- OS-level permissions
- Sandboxing, containerization
- Hypervisor isolation

#### 3. User Boundaries
- **Anonymous → Authenticated**: Unknown to verified
- **User → Administrator**: Standard to privileged
- **Internal → External Users**: Trusted to untrusted

**Security Controls:**
- Authentication mechanisms
- Role-based access control
- Multi-factor authentication

### Analyzing Trust Boundaries

**Questions to Ask:**

1. **Authentication**
   - What authentication is required to cross the boundary?
   - Is it strong enough for the trust level change?

2. **Authorization**
   - What authorization checks are performed?
   - Are permissions verified at every boundary?

3. **Encryption**
   - Is data encrypted when crossing the boundary?
   - What encryption strength is used?

4. **Validation**
   - Are all inputs validated when crossing the boundary?
   - Is validation comprehensive (type, format, range)?

5. **Logging**
   - Is boundary crossing logged and monitored?
   - Can anomalies be detected?

## DFD Best Practices

### Creating Effective DFDs

1. **Start with context diagram**: High-level system overview
2. **Decompose into levels**: Level 0 → Level 1 → Level 2
3. **Focus on data flow**: Not control flow or implementation
4. **Mark trust boundaries explicitly**: Use dashed lines
5. **Label data flows**: Describe what data is moving
6. **Include all external entities**: Don't forget third-party services
7. **Show all data stores**: Databases, caches, files, queues

### Common Mistakes to Avoid

- **Too much detail**: Keep focused on security-relevant flows
- **Missing trust boundaries**: Every boundary is a potential threat point
- **Ignoring indirect flows**: Data flows through logs, caches, etc.
- **Forgetting external dependencies**: Third-party APIs, CDNs, etc.
- **Not updating diagrams**: DFDs must evolve with the system

## Applying STRIDE to DFD

### Systematic Process

For **each element** in the DFD:

1. **External Entity**: Focus on Spoofing, Repudiation
2. **Process**: All STRIDE threats apply
3. **Data Store**: Focus on Tampering, Information Disclosure, Denial of Service
4. **Data Flow**: All STRIDE threats apply
5. **Trust Boundary**: Critical for all STRIDE threats

### Threat Checklist Template

```markdown
## [Data Flow Name]

**Spoofing**: Can the sender be impersonated?
**Tampering**: Can the data be modified in transit?
**Repudiation**: Can the sender deny the action?
**Information Disclosure**: Can the data be intercepted?
**Denial of Service**: Can the flow be disrupted?
**Elevation of Privilege**: Can the flow grant unauthorized access?

**Risk Score**: [Low/Medium/High/Critical]
**Mitigations**: [List of controls]
```
