# RBAC (Role-Based Access Control)

## Service Account Setup

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

## Role and RoleBinding

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

## ClusterRole for Cross-Namespace Access

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

## Advanced RBAC Patterns

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

## Audit RBAC Permissions

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
