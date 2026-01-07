# Image Security

## Image Scanning Policy

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

## Image Pull Policies

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

## Private Registry Authentication

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

## Image Scanning Tools

**Trivy scanning in CI/CD:**

```bash
# Scan image for vulnerabilities
trivy image --severity HIGH,CRITICAL myapp:1.0.0

# Fail build on critical vulnerabilities
trivy image --exit-code 1 --severity CRITICAL myapp:1.0.0
```

**Snyk integration:**

```bash
# Scan Kubernetes manifests
snyk iac test deployment.yaml

# Scan container image
snyk container test myapp:1.0.0
```
