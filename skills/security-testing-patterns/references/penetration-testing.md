# Penetration Testing Techniques

## Reconnaissance and Information Gathering

### Subdomain Enumeration
```bash
# Using subfinder
subfinder -d example.com -o subdomains.txt

# Using amass
amass enum -d example.com -o amass-results.txt

# DNS enumeration
dnsenum example.com
```

### Port Scanning
```bash
# Nmap comprehensive scan
nmap -sV -sC -O -A -p- example.com

# Fast scan of common ports
nmap -F -T4 example.com

# Service version detection
nmap -sV --version-intensity 5 example.com
```

## Vulnerability Assessment

### Web Vulnerability Scanning
```bash
# Nikto web server scanner
nikto -h https://example.com -output nikto-report.html -Format htm

# WPScan for WordPress
wpscan --url https://wordpress.example.com --enumerate ap,at,cb,dbe

# SQLMap for SQL injection
sqlmap -u "https://example.com/page?id=1" --batch --level=5 --risk=3
```

## Manual Testing Techniques

### Authentication Testing Checklist
```javascript
// Test cases for authentication
const authenticationTests = [
  {
    name: "Brute Force Protection",
    test: async () => {
      // Attempt multiple failed logins
      for (let i = 0; i < 10; i++) {
        await login({ username: 'test', password: 'wrong' });
      }
      // Verify account lockout or rate limiting
    }
  },
  {
    name: "Password Reset Token Security",
    test: async () => {
      const token = await requestPasswordReset('user@example.com');
      // Verify token entropy
      // Test token expiration
      // Attempt token reuse
      // Test token predictability
    }
  },
  {
    name: "Session Fixation",
    test: async () => {
      const sessionBefore = getSessionId();
      await login({ username: 'test', password: 'password' });
      const sessionAfter = getSessionId();
      // Verify session ID changes after authentication
      assert(sessionBefore !== sessionAfter);
    }
  },
  {
    name: "Session Timeout",
    test: async () => {
      await login({ username: 'test', password: 'password' });
      await wait(30 * 60 * 1000); // 30 minutes
      // Verify session is invalidated
      const response = await makeAuthenticatedRequest();
      assert(response.status === 401);
    }
  }
];
```

### Authorization Testing
```javascript
// Privilege escalation tests
const authorizationTests = {
  async testHorizontalPrivilegeEscalation() {
    // User A tries to access User B's resources
    const userA = await login({ username: 'userA', password: 'passA' });
    const userBResource = '/api/users/userB/profile';

    const response = await fetch(userBResource, {
      headers: { Authorization: `Bearer ${userA.token}` }
    });

    assert(response.status === 403, 'Horizontal privilege escalation possible');
  },

  async testVerticalPrivilegeEscalation() {
    // Regular user tries to access admin functions
    const regularUser = await login({ username: 'user', password: 'pass' });
    const adminEndpoint = '/api/admin/users';

    const response = await fetch(adminEndpoint, {
      headers: { Authorization: `Bearer ${regularUser.token}` }
    });

    assert(response.status === 403, 'Vertical privilege escalation possible');
  },

  async testInsecureDirectObjectReference() {
    // Test sequential ID enumeration
    const user = await login({ username: 'user', password: 'pass' });

    for (let id = 1; id <= 100; id++) {
      const response = await fetch(`/api/documents/${id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });

      if (response.status === 200) {
        console.log(`IDOR vulnerability: User can access document ${id}`);
      }
    }
  }
};
```

## Reconnaissance Phase

### Passive OSINT

Gather intelligence without direct interaction with the target.

**Domain and infrastructure**:
```bash
# WHOIS lookup
whois example.com

# DNS records (all types)
dig example.com ANY +noall +answer
dig example.com MX
dig example.com TXT

# Certificate transparency logs
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u

# Wayback Machine for historical endpoints
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&output=json&fl=original&collapse=urlkey" | jq -r '.[][]' | sort -u
```

**Employee and organizational OSINT**:
- LinkedIn employee enumeration (job titles, technologies mentioned)
- GitHub/GitLab organization repositories (leaked secrets, internal tooling)
- Pastebin/paste site monitoring for leaked credentials
- Google dorking: `site:example.com filetype:pdf`, `inurl:admin site:example.com`
- Shodan/Censys for exposed services and banners

**Email harvesting**:
```bash
# theHarvester
theHarvester -d example.com -b google,linkedin,dnsdumpster -l 500

# Verify email format
# Common patterns: first.last@, flast@, firstl@
```

### Active Enumeration

Direct interaction with target systems (requires authorization).

```bash
# Subdomain brute-force
gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50

# Virtual host discovery
gobuster vhost -u https://example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Directory and file enumeration
gobuster dir -u https://example.com -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,asp,js,html -t 50

# Technology fingerprinting
whatweb https://example.com
wappalyzer https://example.com
```

### Asset Mapping Methodology

Build a comprehensive target map:

```
1. Enumerate all subdomains (passive + active)
2. Resolve IPs and identify hosting providers
3. Port scan all unique IPs
4. Fingerprint services on open ports
5. Map relationships between assets
6. Identify shared infrastructure
7. Prioritize targets by attack surface area
```

**Asset inventory template**:

| Asset | IP | Ports | Services | Technology | Priority |
|---|---|---|---|---|---|
| www.example.com | 1.2.3.4 | 80, 443 | nginx 1.24 | React, Node.js | High |
| api.example.com | 1.2.3.5 | 443 | Express 4.x | REST API | Critical |
| admin.example.com | 1.2.3.4 | 443 | nginx 1.24 | React, Auth0 | Critical |

## Exploitation Phase

### Vulnerability Validation

Before exploiting, confirm the finding is real and assess safety.

**Validation decision tree**:
```
Is it safe to validate?
  YES -> Can you use a non-destructive PoC?
         YES -> Execute PoC, capture evidence
         NO  -> Document theoretical impact, flag for manual review
  NO  -> Document finding based on version/config evidence only
```

**Safe validation techniques**:
- SQL injection: Use `SLEEP()` or boolean-based detection (no data modification)
- XSS: Use `alert(document.domain)` or harmless payload
- SSRF: Request to an out-of-band collaborator (Burp Collaborator, interactsh)
- RCE: Use `id`, `whoami`, or DNS callback (never destructive commands)
- Auth bypass: Access a test resource, never modify production data

### Exploit Chaining

Combine lower-severity findings into higher-impact attack paths.

**Common chains**:

| Chain | Components | Impact |
|---|---|---|
| SSRF to Cloud Metadata | SSRF + cloud metadata endpoint (169.254.169.254) | AWS keys, full account takeover |
| XSS to Account Takeover | Stored XSS + session token theft | Full user impersonation |
| IDOR to Data Breach | IDOR + API enumeration + no rate limiting | Mass data exfiltration |
| SQLi to RCE | SQL injection + `INTO OUTFILE` or `xp_cmdshell` | Server compromise |
| Open Redirect to Phishing | Open redirect + OAuth token theft | Credential harvesting |

**Chaining methodology**:
1. Map all confirmed vulnerabilities on the attack surface
2. Identify trust relationships between components
3. Determine which findings can be combined for greater impact
4. Build the chain from initial access to objective
5. Test each link individually, then the full chain
6. Document the chain with step-by-step reproduction

### Privilege Escalation Patterns

**Linux**:
```bash
# Enumerate escalation vectors
# SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Writable cron jobs
ls -la /etc/cron* /var/spool/cron/crontabs

# Sudo permissions
sudo -l

# Kernel version (for exploit matching)
uname -a

# Capabilities
getcap -r / 2>/dev/null

# Writable /etc/passwd
ls -la /etc/passwd
```

**Application-level**:
- JWT claim manipulation (change `role: user` to `role: admin`)
- Parameter tampering on role-assignment endpoints
- Mass assignment: include `isAdmin=true` in profile update
- Token scope escalation in OAuth flows
- GraphQL introspection to discover admin mutations

## Reporting Phase

### Finding Severity Classification

Use CVSS v3.1 as the primary scoring system with contextual adjustments.

| Severity | CVSS Range | SLA (Remediation) | Examples |
|---|---|---|---|
| Critical | 9.0 - 10.0 | 24-48 hours | RCE, SQLi with data access, auth bypass to admin |
| High | 7.0 - 8.9 | 1-2 weeks | Stored XSS, SSRF to internal, priv escalation |
| Medium | 4.0 - 6.9 | 1-2 months | Reflected XSS, information disclosure, CSRF |
| Low | 0.1 - 3.9 | Next release | Missing headers, verbose errors, minor info leak |
| Informational | 0.0 | Best effort | Best practice recommendations, hardening suggestions |

### Executive Summary Template

```markdown
## Executive Summary

### Engagement Overview
- **Client**: [name]
- **Assessment Type**: [External/Internal/Web App/API/Full Scope]
- **Testing Period**: [start date] - [end date]
- **Methodology**: OWASP Testing Guide v4, PTES, OSSTMM

### Key Findings

| Severity | Count |
|---|---|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |
| Informational | X |

### Risk Summary
[2-3 sentences describing overall security posture and most impactful findings]

### Top Recommendations
1. [Most critical remediation action]
2. [Second priority]
3. [Third priority]

### Positive Observations
- [Security control that was effective]
- [Good practice observed]
```

### Remediation Tracking

```markdown
## Remediation Tracker

| ID | Finding | Severity | Owner | Status | Retest Date | Result |
|---|---|---|---|---|---|---|
| PT-001 | SQL Injection in search | Critical | @backend | Remediated | 2025-02-15 | Pass |
| PT-002 | Weak session management | High | @auth-team | In Progress | - | - |
| PT-003 | Missing rate limiting | Medium | @api-team | Open | - | - |
```

**Retest protocol**:
1. Verify original exploit no longer works
2. Test common bypass techniques for the same vulnerability class
3. Confirm fix doesn't introduce new issues
4. Update finding status with retest evidence

## 8-Domain Penetration Testing Checklist

### 1. Network

```
[ ] External perimeter scan (all ports)
[ ] Internal network segmentation validation
[ ] Firewall rule review and bypass testing
[ ] VPN configuration and authentication testing
[ ] DNS poisoning and zone transfer attempts
[ ] ARP spoofing and MITM in local segments
[ ] SNMP community string enumeration
[ ] Network service exploitation (SMB, RDP, SSH)
[ ] IPv6 attack surface assessment
[ ] Traffic interception and protocol analysis
```

### 2. Web Application

```
[ ] OWASP Top 10 full assessment
[ ] Input validation on all user-facing fields
[ ] Authentication and session management review
[ ] Authorization and access control testing
[ ] File upload validation and bypass
[ ] Business logic flaw identification
[ ] Client-side security (CSP, SRI, cookie flags)
[ ] HTTP security header validation
[ ] WebSocket security testing
[ ] Server-side template injection (SSTI)
```

### 3. API

```
[ ] Authentication mechanism review (OAuth, JWT, API keys)
[ ] Authorization testing (BOLA, BFLA per OWASP API Top 10)
[ ] Input validation and injection testing on all parameters
[ ] Rate limiting and resource exhaustion testing
[ ] Mass assignment / excessive data exposure
[ ] API versioning and deprecated endpoint access
[ ] GraphQL introspection and query depth limits
[ ] OpenAPI/Swagger spec vs. actual behavior comparison
[ ] CORS policy validation
[ ] Error handling and information leakage
```

### 4. Mobile

```
[ ] Static analysis (decompile, hardcoded secrets, insecure storage)
[ ] Dynamic analysis (runtime manipulation, API traffic)
[ ] Certificate pinning bypass testing
[ ] Local data storage review (SQLite, SharedPreferences, Keychain)
[ ] IPC/intent security (Android) / URL scheme handling (iOS)
[ ] Root/jailbreak detection bypass
[ ] Binary protections (obfuscation, anti-tampering)
[ ] Third-party SDK and library audit
[ ] Push notification security
[ ] Biometric authentication bypass
```

### 5. Cloud

```
[ ] IAM policy review (overprivileged roles, stale credentials)
[ ] S3/Blob storage permissions and public access
[ ] Security group and network ACL review
[ ] Secrets management (no hardcoded keys, rotation policy)
[ ] Logging and monitoring configuration (CloudTrail, GuardDuty)
[ ] Container image vulnerability scanning
[ ] Kubernetes RBAC and pod security policies
[ ] Serverless function permission boundaries
[ ] Database exposure (public endpoints, default credentials)
[ ] Cross-account trust relationship review
```

### 6. Social Engineering

```
[ ] Phishing campaign (email, with click/credential tracking)
[ ] Spear-phishing targeted at high-value personnel
[ ] Vishing (phone-based pretexting) attempts
[ ] USB drop / baiting test
[ ] Pretexting scenarios (impersonation calls)
[ ] Employee security awareness baseline measurement
[ ] Help desk social engineering (password reset requests)
[ ] Third-party vendor impersonation
```

### 7. Physical

```
[ ] Perimeter security assessment (fences, cameras, lighting)
[ ] Badge cloning / tailgating attempts
[ ] Lock bypass testing (pick, shim, bump)
[ ] Dumpster diving for sensitive documents
[ ] Clean desk policy verification
[ ] Server room / data center access controls
[ ] Visitor management process testing
[ ] Wireless access point physical security
```

### 8. Wireless

```
[ ] WiFi network enumeration and mapping
[ ] WPA2/WPA3 authentication attack testing
[ ] Evil twin / rogue access point deployment
[ ] Client isolation verification
[ ] Guest network segmentation validation
[ ] WPS vulnerability testing
[ ] Bluetooth enumeration and pairing attacks
[ ] RF signal analysis and interference testing
[ ] Captive portal bypass attempts
[ ] Hidden SSID discovery
```
