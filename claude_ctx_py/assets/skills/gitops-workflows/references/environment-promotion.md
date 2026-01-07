# Environment Promotion Strategies

## 1. Git-Based Promotion

**Branch-based flow:**
```bash
# Promote staging to production
git checkout main
git merge staging --no-ff -m "Promote staging to production"
git push origin main

# ArgoCD/Flux automatically sync production
```

**Tag-based flow:**
```yaml
# Development tracks main
source:
  targetRevision: main

# Staging tracks release candidates
source:
  targetRevision: v1.2.3-rc1

# Production tracks stable releases
source:
  targetRevision: v1.2.3
```

**Implementation:**
```bash
# Create release candidate
git tag v1.2.3-rc1
git push origin v1.2.3-rc1

# After validation, promote to production
git tag v1.2.3
git push origin v1.2.3
```

## 2. Kustomize Overlay Promotion

**Base configuration:**
```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: app:latest
```

**Environment overlays:**
```yaml
# overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
images:
- name: app
  newTag: v1.2.3-staging
patches:
- patch: |-
    - op: replace
      path: /spec/replicas
      value: 2
  target:
    kind: Deployment

# overlays/production/kustomization.yaml
images:
- name: app
  newTag: v1.2.3  # Promote by updating tag
patches:
- patch: |-
    - op: replace
      path: /spec/replicas
      value: 5
```

## 3. Automated Image Updates (Flux)

**ImageRepository:**
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageRepository
metadata:
  name: frontend
  namespace: flux-system
spec:
  image: gcr.io/org/frontend
  interval: 1m
```

**ImagePolicy:**
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImagePolicy
metadata:
  name: frontend-policy
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: frontend
  policy:
    semver:
      range: 1.x.x  # Only stable 1.x releases
```

**ImageUpdateAutomation:**
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: frontend-automation
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: gitops-repo
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcd@example.com
        name: Flux CD
      messageTemplate: |
        Update {{range .Updated.Images}}{{println .}}{{end}}
    push:
      branch: main
  update:
    path: ./apps/production
    strategy: Setters
```
