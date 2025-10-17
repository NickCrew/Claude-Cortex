---
name: gitops-workflows
description: GitOps workflows and patterns using ArgoCD and Flux for declarative Kubernetes deployments. Use when implementing CI/CD for Kubernetes, managing multi-environment deployments, or adopting declarative infrastructure practices.
---

# GitOps Workflows

Expert guidance for implementing production-grade GitOps workflows using ArgoCD and Flux CD, covering declarative deployment patterns, progressive delivery strategies, multi-environment management, and secure secret handling for Kubernetes infrastructure.

## When to Use This Skill

- Implementing GitOps principles for Kubernetes deployments
- Automating continuous delivery from Git repositories
- Managing multi-cluster or multi-environment deployments
- Implementing progressive delivery (canary, blue-green) strategies
- Configuring automated sync policies and reconciliation
- Managing secrets securely in GitOps workflows
- Setting up environment promotion workflows
- Designing repository structures for GitOps (monorepo vs multi-repo)
- Implementing rollback strategies and disaster recovery
- Establishing compliance and audit trails through Git

## GitOps Core Principles

### OpenGitOps Standards

**1. Declarative**
- Entire desired system state expressed declaratively
- Infrastructure as Code (IaC) describes complete configuration
- No imperative scripts or manual interventions

**2. Versioned and Immutable**
- Canonical desired state stored in Git
- Full audit trail through Git history
- Ability to recreate entire system from repository

**3. Pulled Automatically**
- Software agents automatically pull desired state from Git
- No push-based deployments to production
- Clusters pull changes rather than CI pushing changes

**4. Continuously Reconciled**
- Agents ensure actual state matches desired state
- Automatic drift detection and correction
- Self-healing systems that recover from manual changes

### Benefits

**Operational advantages:**
- Complete deployment history through Git
- Fast rollback via Git revert
- Enhanced security (no cluster credentials in CI)
- Declarative disaster recovery
- Multi-cluster consistency
- Self-healing infrastructure

**Developer advantages:**
- Familiar Git workflows
- Pull request reviews for infrastructure changes
- Automated deployment pipeline
- Environment parity
- Clear change tracking

## Repository Structure Patterns

### 1. Monorepo Pattern

**Structure:**
```
gitops-repo/
├── apps/
│   ├── production/
│   │   ├── frontend/
│   │   │   ├── kustomization.yaml
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   ├── backend/
│   │   └── database/
│   ├── staging/
│   └── development/
├── infrastructure/
│   ├── ingress-nginx/
│   ├── cert-manager/
│   ├── external-secrets/
│   └── monitoring/
│       ├── prometheus/
│       └── grafana/
├── clusters/
│   ├── production/
│   │   └── cluster-config.yaml
│   ├── staging/
│   └── development/
└── base/
    ├── apps/
    └── infrastructure/
```

**Characteristics:**
- Single source of truth
- Shared base configurations via Kustomize
- Easy to see full system state
- Simplified dependency management
- Suitable for small to medium teams

**Best for:** Organizations with unified platform teams, shared infrastructure components, need for consistency across environments

### 2. Multi-Repo Pattern

**Structure:**
```
# Infrastructure repo
infrastructure-gitops/
├── clusters/
│   ├── production/
│   └── staging/
├── shared/
│   ├── ingress/
│   ├── monitoring/
│   └── security/
└── argocd/
    └── applications/

# Application repos
app-frontend-gitops/
├── base/
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── production/
    └── staging/

app-backend-gitops/
├── helm/
│   └── values-{env}.yaml
└── manifests/
```

**Characteristics:**
- Clear separation of concerns
- Team autonomy
- Independent release cycles
- Granular access control
- Scales for large organizations

**Best for:** Large organizations, independent teams, microservices architectures, different compliance requirements per service

### 3. Environment Branches Pattern

**Structure:**
```
app-gitops/
├── main (development)
├── staging (staging env)
└── production (production env)

Each branch contains:
├── manifests/
│   ├── deployment.yaml
│   └── service.yaml
└── config/
    └── values.yaml
```

**Characteristics:**
- Simple mental model
- Built-in promotion via Git merge
- Clear environment separation
- Suitable for Git flow workflows

**Considerations:**
- Can lead to merge conflicts
- Harder to see differences between environments
- Git history per environment not unified

**Best for:** Small teams, simple applications, teams familiar with Git flow

## ArgoCD Implementation

### Installation and Setup

**Standard installation:**
```yaml
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Production ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  ingressClassName: nginx
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              number: 443
  tls:
  - hosts:
    - argocd.example.com
    secretName: argocd-tls
```

### Application Manifest

**Basic application:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: frontend-app
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io  # Enable cascading delete
spec:
  project: production

  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: apps/production/frontend

    # Optional: Helm values
    helm:
      valueFiles:
      - values-production.yaml
      parameters:
      - name: image.tag
        value: v1.2.3

    # Optional: Kustomize
    kustomize:
      images:
      - gcr.io/org/frontend:v1.2.3

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true           # Delete resources removed from Git
      selfHeal: true        # Reconcile manual changes
      allowEmpty: false     # Prevent accidental empty sync

    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    - PruneLast=true

    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas  # Ignore HPA-managed replicas
```

### App of Apps Pattern

**Root application:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: applications
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: argocd/applications
    directory:
      recurse: true
      jsonnet: {}
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Application structure:**
```
argocd/
├── applications/
│   ├── infrastructure.yaml      # Infrastructure apps
│   ├── production-apps.yaml     # Production apps
│   └── staging-apps.yaml        # Staging apps
└── projects/
    ├── infrastructure.yaml
    ├── production.yaml
    └── staging.yaml
```

### ApplicationSet Pattern

**Multi-cluster deployment:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: frontend-multicluster
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: production-east
        url: https://prod-east.k8s.example.com
        environment: production
      - cluster: production-west
        url: https://prod-west.k8s.example.com
        environment: production
      - cluster: staging
        url: https://staging.k8s.example.com
        environment: staging

  template:
    metadata:
      name: 'frontend-{{cluster}}'
    spec:
      project: '{{environment}}'
      source:
        repoURL: https://github.com/org/gitops-repo
        targetRevision: main
        path: 'apps/{{environment}}/frontend'
      destination:
        server: '{{url}}'
        namespace: frontend
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

**Git directory generator:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: all-apps
spec:
  generators:
  - git:
      repoURL: https://github.com/org/gitops-repo
      revision: main
      directories:
      - path: apps/production/*

  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      source:
        repoURL: https://github.com/org/gitops-repo
        targetRevision: main
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated: {}
```

## Flux CD Implementation

### Bootstrap and Setup

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

### Source Definitions

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

### Kustomization Resources

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

### HelmRelease Resources

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

## Environment Promotion Strategies

### 1. Git-Based Promotion

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

### 2. Kustomize Overlay Promotion

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

### 3. Automated Image Updates (Flux)

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

## Secret Management

### 1. Sealed Secrets

**Install controller:**
```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal
```

**Encrypt secrets:**
```bash
# Create regular secret
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml > secret.yaml

# Encrypt for cluster
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git
git add sealed-secret.yaml
git commit -m "Add encrypted database credentials"
```

**SealedSecret manifest:**
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  encryptedData:
    username: AgBj7V8X...
    password: AgCK9Qw2...
  template:
    metadata:
      name: db-credentials
      namespace: production
    type: Opaque
```

### 2. External Secrets Operator

**Install ESO:**
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

**SecretStore (AWS Secrets Manager):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
```

**ExternalSecret:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore

  target:
    name: db-credentials
    creationPolicy: Owner

  data:
  - secretKey: username
    remoteRef:
      key: production/database/credentials
      property: username
  - secretKey: password
    remoteRef:
      key: production/database/credentials
      property: password
```

**ClusterSecretStore (shared):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
```

### 3. SOPS (Secrets Operations)

**Setup (with age encryption):**
```bash
# Install SOPS
brew install sops

# Install age
brew install age

# Generate age key
age-keygen -o key.txt

# Configure .sops.yaml
cat <<EOF > .sops.yaml
creation_rules:
  - path_regex: .*/production/.*
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
EOF
```

**Encrypt secrets:**
```yaml
# Create secret
cat <<EOF > secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
stringData:
  username: admin
  password: supersecret
EOF

# Encrypt with SOPS
sops --encrypt --in-place secret.yaml

# Commit encrypted file
git add secret.yaml
```

**Flux integration:**
```yaml
# Kustomization with SOPS
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age
  sourceRef:
    kind: GitRepository
    name: gitops-repo
```

## Progressive Delivery

### ArgoCD Rollouts (Canary)

**Rollout resource:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: frontend
spec:
  replicas: 10
  revisionHistoryLimit: 3

  selector:
    matchLabels:
      app: frontend

  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: frontend:v2

  strategy:
    canary:
      steps:
      - setWeight: 10          # 10% traffic to new version
      - pause: {duration: 2m}  # Wait 2 minutes
      - setWeight: 25
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 75
      - pause: {duration: 5m}

      # Automated analysis
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: frontend

      # Traffic routing
      trafficRouting:
        istio:
          virtualService:
            name: frontend
            routes:
            - primary
```

**Analysis template:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name

  metrics:
  - name: success-rate
    interval: 1m
    count: 5
    successCondition: result[0] >= 0.95
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(
            http_requests_total{service="{{args.service-name}}",status!~"5.."}[1m]
          )) /
          sum(rate(
            http_requests_total{service="{{args.service-name}}"}[1m]
          ))
```

### Flagger (Flux Progressive Delivery)

**Install Flagger:**
```bash
kubectl apply -k github.com/fluxcd/flagger//kustomize/istio
```

**Canary resource:**
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: frontend
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend

  service:
    port: 80
    targetPort: 8080

  analysis:
    interval: 1m
    threshold: 5          # Number of iterations
    maxWeight: 50         # Max traffic to canary
    stepWeight: 10        # Traffic increase per iteration

    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m

    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://frontend-canary/"
```

## Rollback Strategies

### Git-Based Rollback

**Revert commit:**
```bash
# Find problematic commit
git log --oneline

# Revert specific commit
git revert abc123
git push origin main

# ArgoCD/Flux automatically syncs rollback
```

**Rollback to previous tag:**
```bash
# Production currently on v1.2.3
# Rollback to v1.2.2
git checkout production
git reset --hard v1.2.2
git push --force origin production

# Update Application targetRevision
kubectl patch application frontend \
  -n argocd \
  --type merge \
  -p '{"spec":{"source":{"targetRevision":"v1.2.2"}}}'
```

### ArgoCD Rollback

**History and rollback:**
```bash
# View deployment history
argocd app history frontend

# Rollback to specific revision
argocd app rollback frontend 5

# Rollback to previous revision
argocd app rollback frontend
```

**Automatic rollback:**
```yaml
# Rollout with automatic rollback
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 1

      # Auto-rollback on analysis failure
      abortScaleDownDelaySeconds: 30
```

### Flux Rollback

**Suspend automation:**
```bash
# Suspend Kustomization
flux suspend kustomization frontend

# Manually rollback Deployment
kubectl rollout undo deployment/frontend -n production

# Resume after validation
flux resume kustomization frontend
```

## Best Practices

### Repository Management

1. **Separate application and infrastructure repos** for different ownership and access control
2. **Use semantic versioning** for releases and tags
3. **Implement branch protection** on main branches
4. **Require pull request reviews** for production changes
5. **Tag production releases** for easy rollback reference
6. **Document promotion workflows** in repository README

### Security

1. **Never commit unencrypted secrets** to Git repositories
2. **Use External Secrets Operator** for cloud-native secret management
3. **Implement least-privilege RBAC** for GitOps tools
4. **Enable audit logging** for all sync operations
5. **Use separate service accounts** per application
6. **Scan manifests** for security issues in CI pipeline

### Sync Policies

1. **Use automated sync** for non-production environments
2. **Require manual approval** for production deployments
3. **Configure sync windows** for maintenance periods
4. **Implement health checks** for custom resources
5. **Use selective sync** for large applications
6. **Test sync policies** in staging before production

### Operations

1. **Monitor sync status** with alerting for failures
2. **Implement progressive delivery** for high-risk changes
3. **Test rollback procedures** regularly
4. **Document disaster recovery** processes
5. **Use resource hooks** for migration tasks
6. **Implement backup strategies** for Git repositories

### Multi-Environment

1. **Use consistent naming** across environments
2. **Minimize environment differences** (only necessary variations)
3. **Test promotion workflows** end-to-end
4. **Automate promotion** where possible
5. **Maintain environment parity** to reduce surprises

## Resources

- **OpenGitOps:** https://opengitops.dev/
- **ArgoCD Documentation:** https://argo-cd.readthedocs.io/
- **Flux Documentation:** https://fluxcd.io/docs/
- **ArgoCD Rollouts:** https://argoproj.github.io/argo-rollouts/
- **Flagger:** https://docs.flagger.app/
- **External Secrets Operator:** https://external-secrets.io/
- **Sealed Secrets:** https://github.com/bitnami-labs/sealed-secrets
- **SOPS:** https://github.com/mozilla/sops
