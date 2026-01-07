# Pod Security Standards (PSS/PSA)

## Overview

Pod Security Standards define three policies (Privileged, Baseline, Restricted) enforced through Pod Security Admission (PSA) controller built into Kubernetes 1.23+.

**Three security levels:**
- **Privileged:** Unrestricted (default), allows known privilege escalations
- **Baseline:** Minimally restrictive, prevents known privilege escalations
- **Restricted:** Heavily restricted, follows pod hardening best practices

## Pod Security Admission Configuration

**Namespace-level enforcement:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Enforce restricted policy
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest

    # Audit violations against restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest

    # Warn users about violations
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

**Progressive enforcement strategy:**

```yaml
# Development namespace - warn only
apiVersion: v1
kind: Namespace
metadata:
  name: development
  labels:
    pod-security.kubernetes.io/warn: baseline
    pod-security.kubernetes.io/audit: restricted
---
# Staging namespace - enforce baseline, audit restricted
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
---
# Production namespace - enforce restricted
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Restricted Policy Compliant Pod

**Fully hardened pod specification:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
    spec:
      # Security Context at pod level
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault

      containers:
      - name: app
        image: myapp:1.0.0

        # Security Context at container level
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
          seccompProfile:
            type: RuntimeDefault

        # Resource limits required for restricted
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

        # Writable volumes for read-only filesystem
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache

      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
```

## Migration Strategy

**Audit-first migration approach:**

```bash
# Step 1: Audit all namespaces
kubectl label namespace --all \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

# Step 2: Identify violations
kubectl get pods -A --show-labels | grep "pod-security"

# Step 3: Fix workloads incrementally

# Step 4: Enforce baseline
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=baseline

# Step 5: Eventually enforce restricted
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted
```
