# Reference: Helmfile Patterns

## Helmfile Structure

```yaml
# helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami
  - name: ingress-nginx
    url: https://kubernetes.github.io/ingress-nginx

# Default values for all releases
helmDefaults:
  createNamespace: true
  wait: true
  timeout: 600
  force: false
  atomic: true

# Global values
commonLabels:
  managed-by: helmfile
  environment: {{ .Environment.Name }}

releases:
  # PostgreSQL database
  - name: postgresql
    namespace: database
    chart: bitnami/postgresql
    version: ~12.0.0
    values:
      - auth:
          username: myapp
          database: myapp
          existingSecret: postgresql-secret
      - primary:
          persistence:
            size: 50Gi
    hooks:
      - events: ["presync"]
        command: kubectl
        args: ["create", "namespace", "database", "--dry-run=client", "-o", "yaml"]

  # Application
  - name: my-app
    namespace: {{ .Environment.Name }}
    chart: ./charts/my-app
    values:
      - ./charts/my-app/values.yaml
      - ./environments/{{ .Environment.Name }}/my-app-values.yaml
    secrets:
      - ./environments/{{ .Environment.Name }}/secrets.yaml
    needs:
      - database/postgresql
    set:
      - name: image.tag
        value: {{ requiredEnv "IMAGE_TAG" }}
    hooks:
      - events: ["postsync"]
        command: kubectl
        args: ["rollout", "status", "deployment/my-app", "-n", "{{ .Environment.Name }}"]

  # Ingress controller
  - name: ingress-nginx
    namespace: ingress
    chart: ingress-nginx/ingress-nginx
    version: ~4.0.0
    condition: ingress.enabled
```

## Multi-Environment Configuration

**environments.yaml:**
```yaml
environments:
  development:
    values:
      - environment: development
      - ingress.enabled: false

  staging:
    values:
      - environment: staging
      - ingress.enabled: true
      - replicaCount: 2

  production:
    values:
      - environment: production
      - ingress.enabled: true
      - replicaCount: 5
      - autoscaling.enabled: true
```

## Using Environments

```bash
# Deploy to development
helmfile -e development apply

# Deploy to production
helmfile -e production apply

# Diff before applying
helmfile -e staging diff

# Sync specific release
helmfile -e production -l name=my-app sync
```
