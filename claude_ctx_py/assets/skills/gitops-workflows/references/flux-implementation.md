# Flux CD Implementation

## Bootstrap and Setup

**Bootstrap Flux with GitHub:**
```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap Flux (creates repo structure)
flux bootstrap github \
  --owner=org \
  --repository=gitops-repo \
  --branch=main \
  --path=clusters/production \
  --personal=false \
  --token-auth
```

**Bootstrap result:**
```
clusters/production/
├── flux-system/
│   ├── gotk-components.yaml
│   ├── gotk-sync.yaml
│   └── kustomization.yaml
```

## Source Definitions

**GitRepository source:**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: frontend-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/frontend-app
  ref:
    branch: main
  secretRef:
    name: github-token
  ignore: |
    # Exclude non-deployment files
    /*.md
    /docs/
```

**HelmRepository source:**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 10m
  url: https://charts.bitnami.com/bitnami
```

**OCIRepository source:**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: OCIRepository
metadata:
  name: app-manifests
  namespace: flux-system
spec:
  interval: 5m
  url: oci://ghcr.io/org/manifests
  ref:
    tag: latest
```

## Kustomization Resources

**Application deployment:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: frontend-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./deploy/production
  prune: true
  wait: true
  timeout: 5m

  sourceRef:
    kind: GitRepository
    name: frontend-app

  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: frontend
    namespace: production

  patches:
  - patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: frontend
      spec:
        replicas: 5
    target:
      kind: Deployment
      name: frontend
```

**Dependency management:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app-stack
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps
  prune: true
  sourceRef:
    kind: GitRepository
    name: gitops-repo

  # Wait for infrastructure
  dependsOn:
  - name: infrastructure
  - name: databases
```

## HelmRelease Resources

**Deploying Helm charts:**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: nginx-ingress
  namespace: flux-system
spec:
  interval: 10m
  chart:
    spec:
      chart: ingress-nginx
      version: '4.8.x'
      sourceRef:
        kind: HelmRepository
        name: ingress-nginx
        namespace: flux-system

  values:
    controller:
      replicaCount: 3
      metrics:
        enabled: true

  # Override values from ConfigMap
  valuesFrom:
  - kind: ConfigMap
    name: nginx-values
    valuesKey: values.yaml
```
