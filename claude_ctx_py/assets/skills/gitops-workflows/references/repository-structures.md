# Repository Structure Patterns

## 1. Monorepo Pattern

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

## 2. Multi-Repo Pattern

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

## 3. Environment Branches Pattern

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
