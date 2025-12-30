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
