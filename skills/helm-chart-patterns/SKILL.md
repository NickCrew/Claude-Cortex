---
name: helm-chart-patterns
description: Helm chart development patterns for packaging and deploying Kubernetes applications. Use when creating reusable Helm charts, managing multi-environment deployments, or building application catalogs for Kubernetes.
---

# Helm Chart Patterns

Expert guidance for developing production-grade Helm charts covering chart structure, templating patterns, multi-environment configuration, dependency management, testing strategies, and distribution workflows for Kubernetes application packaging.

## When to Use This Skill

- Creating reusable Helm charts for applications and services
- Building application catalogs and chart repositories
- Managing multi-environment deployments (dev, staging, production)
- Implementing advanced templating with conditionals and loops
- Managing chart dependencies and subcharts
- Implementing chart hooks for lifecycle management
- Testing and validating chart templates
- Packaging and distributing charts via repositories
- Using Helmfile for multi-chart orchestration

## Chart Structure Foundations

### Standard Chart Layout

```
my-app/
├── Chart.yaml              # Chart metadata (required)
├── Chart.lock              # Dependency lock file (generated)
├── values.yaml             # Default configuration (required)
├── values.schema.json      # Values validation schema
├── README.md               # Chart documentation
├── .helmignore             # Packaging exclusions
├── charts/                 # Dependency charts
│   └── postgresql-12.0.0.tgz
├── crds/                   # Custom Resource Definitions
│   └── my-crd.yaml
├── templates/              # K8s manifest templates (required)
│   ├── NOTES.txt          # Post-install instructions
│   ├── _helpers.tpl       # Template functions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── serviceaccount.yaml
│   ├── hpa.yaml
│   └── tests/
│       └── test-connection.yaml
└── files/                  # Static files to include
    └── config/
        └── app.conf
```

### Chart.yaml Configuration

```yaml
apiVersion: v2
name: my-application
version: 1.2.3                    # Chart version (SemVer)
appVersion: "2.5.0"              # Application version
description: Production-ready web application chart
type: application                 # application or library
keywords:
  - web
  - api
  - microservices
home: https://example.com
sources:
  - https://github.com/example/my-app
maintainers:
  - name: Platform Team
    email: platform@example.com
icon: https://example.com/icon.png
kubeVersion: ">=1.24.0-0"        # Compatible K8s versions
dependencies:
  - name: postgresql
    version: "~12.0.0"           # Semver range
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    tags:
      - database
    import-values:
      - child: auth
        parent: postgresql.auth
annotations:
  category: ApplicationServer
  licenses: Apache-2.0
```

**Chart types:**
- `application`: Standard deployable charts
- `library`: Reusable template helpers (not installable)

**Version constraints:**
- Use SemVer for chart versions
- Use constraints for dependencies: `~1.2.3` (>=1.2.3, <1.3.0), `^1.2.3` (>=1.2.3, <2.0.0)

## Values File Patterns

### Hierarchical Values Organization

```yaml
# values.yaml - Production-ready defaults

# Global values (shared with all subcharts)
global:
  imageRegistry: docker.io
  imagePullSecrets: []
  storageClass: ""

# Common labels applied to all resources
commonLabels:
  team: platform
  cost-center: engineering

# Image configuration
image:
  registry: docker.io
  repository: mycompany/app
  tag: ""  # Defaults to .Chart.AppVersion if empty
  pullPolicy: IfNotPresent
  pullSecrets: []

# Deployment configuration
replicaCount: 3
revisionHistoryLimit: 10
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0

# Pod configuration
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
podLabels: {}
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

# Container security context
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
      - ALL

# Service configuration
service:
  enabled: true
  type: ClusterIP
  port: 80
  targetPort: http
  annotations: {}
  sessionAffinity: None

# Ingress configuration
ingress:
  enabled: false
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.example.com

# Resource management
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

# Autoscaling
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 75
  targetMemoryUtilizationPercentage: 80

# Health checks
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /startup
    port: http
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30

# Persistence
persistence:
  enabled: false
  storageClass: ""
  accessMode: ReadWriteOnce
  size: 8Gi
  annotations: {}
  existingClaim: ""

# Node selection
nodeSelector: {}
tolerations: []
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: my-app
          topologyKey: kubernetes.io/hostname

# Service Account
serviceAccount:
  create: true
  annotations: {}
  name: ""
  automountServiceAccountToken: false

# Configuration
config:
  LOG_LEVEL: info
  DATABASE_POOL_SIZE: "10"
  CACHE_TTL: "3600"

# Secrets (use external secret management in production)
secrets: {}

# Monitoring
metrics:
  enabled: false
  serviceMonitor:
    enabled: false
    interval: 30s
    scrapeTimeout: 10s

# Pod Disruption Budget
podDisruptionBudget:
  enabled: true
  minAvailable: 1
  # maxUnavailable: 1

# Network Policy
networkPolicy:
  enabled: false
  policyTypes:
    - Ingress
    - Egress
  ingress: []
  egress: []
```

### Environment-Specific Values

**values-dev.yaml:**
```yaml
replicaCount: 1
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
config:
  LOG_LEVEL: debug
```

**values-production.yaml:**
```yaml
replicaCount: 5
autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi
config:
  LOG_LEVEL: warn
ingress:
  enabled: true
podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

### Values Schema Validation

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image", "service"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Number of pod replicas"
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {
          "type": "string",
          "pattern": "^[a-z0-9-./]+$"
        },
        "tag": {
          "type": "string"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    },
    "service": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ClusterIP", "NodePort", "LoadBalancer"]
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    },
    "resources": {
      "type": "object",
      "properties": {
        "limits": {
          "type": "object",
          "properties": {
            "cpu": {"type": "string"},
            "memory": {"type": "string"}
          }
        },
        "requests": {
          "type": "object",
          "required": ["cpu", "memory"],
          "properties": {
            "cpu": {"type": "string"},
            "memory": {"type": "string"}
          }
        }
      }
    }
  }
}
```

## Template Patterns

### Helper Templates (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Chart name and version label.
*/}}
{{- define "my-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.chart" . }}
{{ include "my-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Service account name
*/}}
{{- define "my-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "my-app.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{/*
Image reference
*/}}
{{- define "my-app.image" -}}
{{- $registry := .Values.global.imageRegistry | default .Values.image.registry -}}
{{- $repository := .Values.image.repository -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry $repository $tag -}}
{{- else -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end -}}
{{- end -}}

{{/*
Image pull secrets
*/}}
{{- define "my-app.imagePullSecrets" -}}
{{- $secrets := concat (.Values.global.imagePullSecrets | default list) (.Values.image.pullSecrets | default list) -}}
{{- if $secrets }}
imagePullSecrets:
{{- range $secrets }}
  - name: {{ . }}
{{- end }}
{{- end }}
{{- end -}}

{{/*
Return true if a ConfigMap should be created
*/}}
{{- define "my-app.createConfigMap" -}}
{{- if or .Values.config .Values.extraConfig -}}
true
{{- end -}}
{{- end -}}
```

### Conditionals and Flow Control

**Conditional resource creation:**
```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "my-app.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

**Multiple conditions:**
```yaml
{{- if and .Values.metrics.enabled .Values.metrics.serviceMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "my-app.fullname" . }}
spec:
  endpoints:
  - port: metrics
    interval: {{ .Values.metrics.serviceMonitor.interval }}
{{- end }}
```

**if-else chains:**
```yaml
resources:
  {{- if .Values.resources }}
  {{- toYaml .Values.resources | nindent 2 }}
  {{- else if eq .Values.environment "production" }}
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
  {{- else }}
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
  {{- end }}
```

### Loops and Iteration

**Range over lists:**
```yaml
{{- range .Values.extraEnvVars }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}

{{- range $key, $value := .Values.config }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}
```

**Creating multiple resources:**
```yaml
{{- range .Values.services }}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ include "my-app.fullname" $ }}-{{ .name }}
  labels:
    {{- include "my-app.labels" $ | nindent 4 }}
    service: {{ .name }}
spec:
  type: {{ .type | default "ClusterIP" }}
  ports:
    - port: {{ .port }}
      targetPort: {{ .targetPort }}
      protocol: TCP
      name: {{ .name }}
  selector:
    {{- include "my-app.selectorLabels" $ | nindent 4 }}
{{- end }}
```

**Indexed loops:**
```yaml
{{- range $index, $replica := until (int .Values.replicaCount) }}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-app.fullname" $ }}-{{ $index }}
data:
  replica-id: {{ $index | quote }}
{{- end }}
```

### Template Functions

**String manipulation:**
```yaml
# Quotes
name: {{ .Values.name | quote }}
name: {{ .Values.name | squote }}  # Single quotes

# Case conversion
name: {{ .Values.name | upper }}
name: {{ .Values.name | lower }}
name: {{ .Values.name | title }}

# Trimming
name: {{ .Values.name | trim }}
name: {{ .Values.name | trimPrefix "-" }}
name: {{ .Values.name | trimSuffix "-" }}
name: {{ .Values.name | trunc 63 }}

# Replacement
name: {{ .Values.name | replace "." "-" }}
```

**Encoding and hashing:**
```yaml
# Base64 encoding
data:
  config: {{ .Values.config | b64enc }}

# SHA256 checksum (for triggering updates)
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

**Type conversion:**
```yaml
# Defaults and coalesce
value: {{ .Values.custom | default "default-value" }}
value: {{ coalesce .Values.a .Values.b .Values.c "fallback" }}

# Type assertions
replicas: {{ .Values.replicaCount | int }}
enabled: {{ .Values.enabled | ternary "yes" "no" }}
```

**Logical operators:**
```yaml
{{- if and .Values.enabled (eq .Values.type "web") }}
{{- if or .Values.devMode (eq .Values.env "development") }}
{{- if not .Values.disabled }}
```

## Dependencies and Subcharts

### Declaring Dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "~12.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    tags:
      - database
    import-values:
      - child: auth
        parent: postgresql.auth

  - name: redis
    version: "^17.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    tags:
      - cache
```

### Managing Dependencies

```bash
# Update and download dependencies
helm dependency update

# List dependencies
helm dependency list

# Build dependencies from charts/ directory
helm dependency build
```

### Subchart Values

**Parent values.yaml:**
```yaml
# Configure subchart directly
postgresql:
  enabled: true
  auth:
    username: myapp
    password: secret123
    database: myapp
  primary:
    persistence:
      size: 10Gi

# Import values from subchart
postgresql.auth: {}  # Will receive imported values

# Global values shared with all subcharts
global:
  imageRegistry: docker.io
  storageClass: fast-ssd
```

### Accessing Parent Values from Subcharts

**Parent's _helpers.tpl:**
```yaml
{{- define "my-app.postgresql.host" -}}
{{- if .Values.postgresql.enabled -}}
{{- printf "%s-postgresql" (include "my-app.fullname" .) -}}
{{- else -}}
{{- .Values.externalDatabase.host -}}
{{- end -}}
{{- end -}}
```

### Library Charts

**Creating a library chart:**
```yaml
# library-chart/Chart.yaml
apiVersion: v2
name: common-templates
version: 1.0.0
type: library
```

**library-chart/templates/_deployment.tpl:**
```yaml
{{- define "common.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "common.fullname" . }}
  labels:
    {{- include "common.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "common.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "common.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: {{ .Values.image }}
        ports:
        - containerPort: {{ .Values.port }}
{{- end -}}
```

**Using library chart:**
```yaml
# Chart.yaml
dependencies:
  - name: common-templates
    version: "1.0.0"
    repository: "https://charts.example.com"
```

```yaml
# templates/deployment.yaml
{{- include "common.deployment" . }}
```

## Hooks and Lifecycle Management

### Hook Types

**Pre-install hook (database migration):**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    metadata:
      name: {{ include "my-app.fullname" . }}-migration
    spec:
      restartPolicy: Never
      containers:
      - name: migration
        image: {{ include "my-app.image" . }}
        command:
          - /bin/sh
          - -c
          - |
            echo "Running database migrations..."
            npm run migrate
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: {{ include "my-app.fullname" . }}
                key: database-url
```

**Post-install hook (smoke tests):**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-smoke-test
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: test
        image: curlimages/curl:latest
        command:
          - sh
          - -c
          - |
            until curl -f http://{{ include "my-app.fullname" . }}:{{ .Values.service.port }}/health; do
              echo "Waiting for service..."
              sleep 5
            done
            echo "Service is healthy!"
```

**Pre-delete hook (backup):**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-backup
  annotations:
    "helm.sh/hook": pre-delete
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: backup
        image: {{ include "my-app.image" . }}
        command: ["/scripts/backup.sh"]
```

**Available hooks:**
- `pre-install`, `post-install`
- `pre-delete`, `post-delete`
- `pre-upgrade`, `post-upgrade`
- `pre-rollback`, `post-rollback`
- `test` (run with `helm test`)

**Hook weights:** Control execution order (-2147483648 to 2147483647, lower first)

**Deletion policies:**
- `before-hook-creation`: Delete previous hook before new one
- `hook-succeeded`: Delete after successful execution
- `hook-failed`: Delete if hook fails

## Testing Patterns

### Chart Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
  - name: wget
    image: busybox:latest
    command: ['wget']
    args: ['{{ include "my-app.fullname" . }}:{{ .Values.service.port }}']
```

```yaml
# templates/tests/test-authentication.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-auth"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
  - name: test
    image: curlimages/curl:latest
    command:
      - sh
      - -c
      - |
        TOKEN=$(curl -s -X POST {{ include "my-app.fullname" . }}/auth/token -d '{"user":"test"}' | jq -r .token)
        curl -f -H "Authorization: Bearer $TOKEN" {{ include "my-app.fullname" . }}/api/protected
```

### Running Tests

```bash
# Install and run tests
helm install my-app ./my-app
helm test my-app

# Show test logs
helm test my-app --logs

# Cleanup after tests
helm test my-app --cleanup
```

### Template Linting and Validation

```bash
# Lint chart for issues
helm lint ./my-app

# Lint with custom values
helm lint ./my-app -f values-production.yaml

# Template rendering (dry-run)
helm template my-app ./my-app

# Template with specific values
helm template my-app ./my-app \
  --set replicaCount=5 \
  -f values-production.yaml

# Validate against cluster
helm install my-app ./my-app --dry-run --debug

# Schema validation
helm lint ./my-app --strict
```

## Packaging and Distribution

### Packaging Charts

```bash
# Package chart
helm package ./my-app

# Package with specific version
helm package ./my-app --version 1.2.3

# Package with dependency update
helm package ./my-app --dependency-update

# Sign package
helm package ./my-app --sign --key 'my-key' --keyring ~/.gnupg/secring.gpg
```

### Chart Repositories

**Creating repository index:**
```bash
# Create index.yaml
helm repo index . --url https://charts.example.com

# Update existing index
helm repo index . --url https://charts.example.com --merge index.yaml
```

**index.yaml structure:**
```yaml
apiVersion: v1
entries:
  my-app:
  - apiVersion: v2
    appVersion: "2.5.0"
    created: "2024-01-01T00:00:00Z"
    description: Production-ready web application chart
    digest: sha256:abcd1234...
    name: my-app
    urls:
    - https://charts.example.com/my-app-1.2.3.tgz
    version: 1.2.3
```

**Using repositories:**
```bash
# Add repository
helm repo add myrepo https://charts.example.com

# Update repository cache
helm repo update

# Search repository
helm repo search myrepo/

# Install from repository
helm install my-app myrepo/my-app --version 1.2.3
```

### OCI Registry Support

```bash
# Login to OCI registry
helm registry login registry.example.com

# Package and push
helm package ./my-app
helm push my-app-1.2.3.tgz oci://registry.example.com/charts

# Install from OCI
helm install my-app oci://registry.example.com/charts/my-app --version 1.2.3

# Pull chart
helm pull oci://registry.example.com/charts/my-app --version 1.2.3
```

## Helmfile Patterns

### Helmfile Structure

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

### Multi-Environment Configuration

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

**Using environments:**
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

## Best Practices Summary

### Template Best Practices

1. **Use helper templates** for repeated logic
2. **Quote all strings**: `{{ .Values.name | quote }}`
3. **Validate with schema**: Always include values.schema.json
4. **Document all values**: Add comments in values.yaml
5. **Use consistent indentation**: `nindent` for proper YAML formatting
6. **Check for nil**: `{{- if .Values.optional }}` before accessing nested values
7. **Use `required`**: `{{ required "message" .Values.critical }}`

### Versioning and Compatibility

1. **Follow SemVer** for chart versions
2. **Pin dependencies** to specific versions or ranges
3. **Test upgrades** from previous versions
4. **Document breaking changes** in README
5. **Use appVersion** to track application version separately
6. **Set kubeVersion** to declare K8s compatibility

### Security Considerations

1. **Never commit secrets** to values files
2. **Use external secret management**: Sealed Secrets, External Secrets Operator
3. **Set security contexts** in all pods
4. **Drop capabilities**: `capabilities.drop: [ALL]`
5. **Use non-root users**: `runAsNonRoot: true`
6. **Enable seccomp**: `seccompProfile.type: RuntimeDefault`
7. **Sign packages** for production distribution

### Testing Strategy

1. **Lint before packaging**: `helm lint`
2. **Validate templates**: `helm template --debug`
3. **Test installations**: `helm test`
4. **Dry-run upgrades**: `helm upgrade --dry-run`
5. **Use CI/CD pipelines** for automated testing
6. **Test with multiple value combinations**

## Resources

- **Helm Documentation**: https://helm.sh/docs/
- **Chart Template Guide**: https://helm.sh/docs/chart_template_guide/
- **Best Practices**: https://helm.sh/docs/chart_best_practices/
- **Helmfile**: https://github.com/helmfile/helmfile
- **Chart Testing**: https://github.com/helm/chart-testing
