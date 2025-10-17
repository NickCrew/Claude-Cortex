---
name: kubernetes-security-policies
description: Kubernetes security policies, RBAC, and Pod Security Standards for hardened cluster deployments. Use when implementing cluster security, defining network policies, or enforcing security compliance in Kubernetes environments.
---

# Kubernetes Security Policies

Comprehensive guidance for implementing security policies in Kubernetes clusters, covering Pod Security Standards, Network Policies, RBAC, Security Contexts, admission control, secrets management, and runtime security for production-grade hardened deployments.

## When to Use This Skill

- Implementing Pod Security Standards (PSS/PSA) across namespaces
- Designing and enforcing Network Policies for micro-segmentation
- Configuring RBAC with least-privilege access control
- Setting Security Contexts for container hardening
- Deploying admission controllers (OPA/Gatekeeper, Kyverno)
- Managing secrets and sensitive data securely
- Implementing image security and vulnerability scanning
- Enforcing runtime security policies and threat detection
- Meeting compliance requirements (CIS, NIST, PCI-DSS, SOC2)
- Conducting security audits and hardening assessments

## Pod Security Standards (PSS/PSA)

### Overview

Pod Security Standards define three policies (Privileged, Baseline, Restricted) enforced through Pod Security Admission (PSA) controller built into Kubernetes 1.23+.

**Three security levels:**
- **Privileged:** Unrestricted (default), allows known privilege escalations
- **Baseline:** Minimally restrictive, prevents known privilege escalations
- **Restricted:** Heavily restricted, follows pod hardening best practices

### Pod Security Admission Configuration

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

### Restricted Policy Compliant Pod

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

### Migration Strategy

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

## Network Policies

### Default Deny Policy

**Start with zero-trust default deny:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress
```

### Allow Specific Ingress Traffic

**Frontend to backend communication:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress

  ingress:
  # Allow from frontend pods
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

  # Allow from ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080

  egress:
  # Allow to database
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432

  # Allow DNS queries
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

  # Allow HTTPS to external services
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### Database Isolation Policy

**Strict database access control:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  - Egress

  ingress:
  # Only allow from specific app pods
  - from:
    - podSelector:
        matchLabels:
          app: backend
          tier: api
    ports:
    - protocol: TCP
      port: 5432

  egress:
  # Deny all egress (database shouldn't initiate connections)
  []
```

### Multi-Namespace Communication

**Cross-namespace communication with namespace selectors:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-monitoring
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress

  ingress:
  # Allow Prometheus from monitoring namespace
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
      podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 8080  # Metrics endpoint
```

## RBAC (Role-Based Access Control)

### Service Account Setup

**Principle of least privilege:**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
automountServiceAccountToken: false  # Explicit opt-in
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: production
spec:
  template:
    spec:
      serviceAccountName: app-sa
      automountServiceAccountToken: true  # Only if needed
```

### Role and RoleBinding

**Namespace-scoped permissions:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
# Read-only access to pods
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

# Read pod logs
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-pod-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ClusterRole for Cross-Namespace Access

**Cluster-wide permissions (use sparingly):**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
# Read nodes and metrics
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["metrics.k8s.io"]
  resources: ["nodes"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-node-reader
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

### Advanced RBAC Patterns

**Application-specific permissions:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-operator
  namespace: production
rules:
# Manage ConfigMaps for dynamic config
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "update", "patch"]
  resourceNames: ["app-config"]  # Restrict to specific ConfigMap

# Read secrets (no write)
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["app-credentials"]

# Create/delete ephemeral pods for batch jobs
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "delete", "get", "list", "watch"]

# Access own deployment for rollout status
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
  resourceNames: ["app"]
```

### Audit RBAC Permissions

```bash
# Check what a service account can do
kubectl auth can-i --list --as=system:serviceaccount:production:app-sa

# Check specific permission
kubectl auth can-i delete pods \
  --as=system:serviceaccount:production:app-sa \
  -n production

# Audit all ClusterRoleBindings
kubectl get clusterrolebindings -o json | \
  jq -r '.items[] | select(.subjects[]?.kind=="ServiceAccount") |
  "\(.metadata.name): \(.subjects[].namespace)/\(.subjects[].name)"'
```

## Security Contexts

### Container Security Context

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

### Capability Management

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

### Seccomp Profiles

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

## Admission Control

### OPA Gatekeeper Policies

**Install Gatekeeper:**

```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
```

**Constraint Template:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels

      violation[{"msg": msg, "details": {"missing_labels": missing}}] {
        provided := {label | input.review.object.metadata.labels[label]}
        required := {label | label := input.parameters.labels[_]}
        missing := required - provided
        count(missing) > 0
        msg := sprintf("Missing required labels: %v", [missing])
      }
```

**Enforce the constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-app-labels
spec:
  match:
    kinds:
    - apiGroups: ["apps"]
      kinds: ["Deployment", "StatefulSet"]
    namespaces:
    - production
  parameters:
    labels:
    - "app"
    - "team"
    - "environment"
```

**Deny privileged containers:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowprivileged
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowPrivileged
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8sdisallowprivileged

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        container.securityContext.privileged
        msg := sprintf("Container %v is privileged", [container.name])
      }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sDisallowPrivileged
metadata:
  name: deny-privileged-containers
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
    excludedNamespaces:
    - kube-system
```

### Kyverno Policies

**Install Kyverno:**

```bash
kubectl create -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml
```

**Require resource limits:**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-limits
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: require-cpu-memory-limits
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "CPU and memory limits are required"
      pattern:
        spec:
          containers:
          - resources:
              limits:
                memory: "?*"
                cpu: "?*"
```

**Disallow latest tag:**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-image-tag
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Images must specify a tag other than 'latest'"
      pattern:
        spec:
          containers:
          - image: "!*:latest"
```

**Mutate to add security context:**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-security-context
spec:
  rules:
  - name: add-non-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    mutate:
      patchStrategicMerge:
        spec:
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
          containers:
          - (name): "*"
            securityContext:
              allowPrivilegeEscalation: false
              readOnlyRootFilesystem: true
              capabilities:
                drop:
                - ALL
```

## Secrets Management

### Kubernetes Secrets Best Practices

**Base64 is not encryption - use external secret management:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-credentials
  namespace: production
type: Opaque
stringData:  # Use stringData for clarity
  username: admin
  password: supersecret
  database-url: postgresql://admin:supersecret@db:5432/myapp
```

### External Secrets Operator

**Sync from AWS Secrets Manager:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secretsmanager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: app-credentials
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: prod/app/database
      property: password
```

### Sealed Secrets

**Encrypt secrets for GitOps:**

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal

# Create and seal a secret
kubectl create secret generic app-secret \
  --from-literal=api-key=secret123 \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git (safe)
```

**SealedSecret manifest:**

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: app-secret
  namespace: production
spec:
  encryptedData:
    api-key: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
  template:
    metadata:
      name: app-secret
      namespace: production
    type: Opaque
```

### HashiCorp Vault Integration

**Vault Agent Injector:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "app-role"
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/app/config"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/app/config" -}}
          export DB_PASSWORD="{{ .Data.data.password }}"
          export API_KEY="{{ .Data.data.api_key }}"
          {{- end }}
    spec:
      serviceAccountName: app
      containers:
      - name: app
        image: app:1.0
        command: ["/bin/sh"]
        args: ["-c", "source /vault/secrets/config && ./app"]
```

## Image Security

### Image Scanning Policy

**Enforce scanned images with Kyverno:**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-signature
    match:
      any:
      - resources:
          kinds:
          - Pod
    verifyImages:
    - imageReferences:
      - "registry.example.com/*"
      attestors:
      - count: 1
        entries:
        - keys:
            publicKeys: |
              -----BEGIN PUBLIC KEY-----
              MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
              -----END PUBLIC KEY-----
```

### Image Pull Policies

**Immutable image digests:**

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      # BAD: Mutable tag
      - name: app
        image: app:v1.0.0

      # GOOD: Immutable digest
      - name: app
        image: app@sha256:abc123def456...
        imagePullPolicy: IfNotPresent
```

### Private Registry Authentication

**Image pull secrets:**

```bash
# Create docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=robot \
  --docker-password=secret \
  --docker-email=team@example.com \
  -n production
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
imagePullSecrets:
- name: regcred
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      serviceAccountName: app-sa
```

## Best Practices Summary

### Security Hardening Checklist

**Pod Security:**
- [ ] Enable Pod Security Admission (restricted policy)
- [ ] Run as non-root user (runAsNonRoot: true)
- [ ] Read-only root filesystem (readOnlyRootFilesystem: true)
- [ ] Drop all capabilities, add only required
- [ ] Enable seccomp RuntimeDefault profile
- [ ] Disable privilege escalation (allowPrivilegeEscalation: false)
- [ ] Set resource requests and limits

**Network Security:**
- [ ] Implement default-deny network policies
- [ ] Create explicit allow rules for required traffic
- [ ] Isolate namespaces with network segmentation
- [ ] Use service mesh for mTLS between services
- [ ] Restrict egress to known external endpoints

**Access Control:**
- [ ] Implement RBAC with least privilege
- [ ] Use dedicated service accounts per application
- [ ] Disable automountServiceAccountToken by default
- [ ] Audit and minimize ClusterRole/ClusterRoleBinding usage
- [ ] Rotate service account tokens regularly

**Secrets Management:**
- [ ] Never commit secrets to Git
- [ ] Use external secret management (Vault, ESO)
- [ ] Encrypt secrets at rest in etcd
- [ ] Mount secrets as files, not environment variables
- [ ] Rotate secrets regularly
- [ ] Implement secret access auditing

**Admission Control:**
- [ ] Deploy policy engine (OPA Gatekeeper or Kyverno)
- [ ] Enforce image signature verification
- [ ] Require resource limits on all pods
- [ ] Disallow privileged containers
- [ ] Require security contexts
- [ ] Block deprecated API versions

**Image Security:**
- [ ] Scan images for vulnerabilities (Trivy, Snyk, Clair)
- [ ] Use minimal base images (distroless, Alpine)
- [ ] Sign images with Sigstore/Cosign
- [ ] Use immutable image digests
- [ ] Implement image promotion pipeline
- [ ] Regularly update base images

**Runtime Security:**
- [ ] Deploy runtime security tool (Falco, Sysdig)
- [ ] Monitor for anomalous behavior
- [ ] Enable audit logging
- [ ] Implement intrusion detection
- [ ] Configure alerts for security events

### Common Security Anti-Patterns

1. **Running as root:** Always set runAsNonRoot: true
2. **Privileged containers:** Avoid unless absolutely necessary
3. **Host network/IPC/PID:** Creates shared fate with host
4. **HostPath volumes:** Security risk, avoid in production
5. **Latest image tag:** Not immutable, breaks reproducibility
6. **Secrets in env vars:** Visible in process listings
7. **No network policies:** Unrestricted pod-to-pod traffic
8. **Overly permissive RBAC:** Violates least privilege
9. **No admission control:** Can't enforce policies
10. **Disabled Pod Security:** Allows insecure pod specs

### Compliance Frameworks

**CIS Kubernetes Benchmark:**
- Automated with tools like kube-bench
- Covers control plane, etcd, kubelet, policies
- Regular assessments recommended

**NIST SP 800-190:**
- Container security guidance
- Image, runtime, orchestration controls
- Supply chain security

**PCI-DSS for Kubernetes:**
- Network segmentation requirements
- Access control standards
- Audit logging mandates
- Encryption requirements

## Resources

- **Pod Security Standards:** https://kubernetes.io/docs/concepts/security/pod-security-standards/
- **Network Policies:** https://kubernetes.io/docs/concepts/services-networking/network-policies/
- **RBAC:** https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- **OPA Gatekeeper:** https://open-policy-agent.github.io/gatekeeper/
- **Kyverno:** https://kyverno.io/docs/
- **External Secrets Operator:** https://external-secrets.io/
- **Falco Runtime Security:** https://falco.org/docs/
- **CIS Benchmarks:** https://www.cisecurity.org/benchmark/kubernetes
- **NSA/CISA Kubernetes Hardening Guide:** https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF
