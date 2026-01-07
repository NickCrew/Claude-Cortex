# Security Contexts

## Container Security Context

**Comprehensive container hardening:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    # Pod-level settings
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    fsGroupChangePolicy: "OnRootMismatch"
    seccompProfile:
      type: RuntimeDefault
    supplementalGroups: [2000]

  containers:
  - name: app
    image: app:1.0
    securityContext:
      # Container-level (overrides pod-level)
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true

      # Drop all capabilities, add only required
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE  # Only if binding to port <1024

      # Seccomp profile
      seccompProfile:
        type: RuntimeDefault
```

## Capability Management

**Minimal capability sets:**

```yaml
# Web server needing port 80/443
securityContext:
  capabilities:
    drop:
    - ALL
    add:
    - NET_BIND_SERVICE
    - CHOWN
    - SETGID
    - SETUID
---
# Application with no special privileges
securityContext:
  capabilities:
    drop:
    - ALL  # Drop all, add none
```

## Seccomp Profiles

**Custom seccomp profile:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-seccomp
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/app-seccomp.json
  containers:
  - name: app
    image: app:1.0
```

**Example seccomp profile (profiles/app-seccomp.json):**
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat",
        "fstat", "lstat", "poll", "lseek", "mmap",
        "mprotect", "munmap", "brk", "rt_sigaction",
        "rt_sigprocmask", "ioctl", "access", "socket",
        "connect", "accept", "sendto", "recvfrom"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```
