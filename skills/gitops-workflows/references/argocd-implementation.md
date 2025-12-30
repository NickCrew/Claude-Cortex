# ArgoCD Implementation

## Installation and Setup

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

## Application Manifest

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

## App of Apps Pattern

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

## ApplicationSet Pattern

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
