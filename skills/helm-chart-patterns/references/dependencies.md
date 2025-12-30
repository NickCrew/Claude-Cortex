# Reference: Dependencies and Subcharts

## Declaring Dependencies

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

## Managing Dependencies

```bash
# Update and download dependencies
helm dependency update

# List dependencies
helm dependency list

# Build dependencies from charts/ directory
helm dependency build
```

## Subchart Values

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

## Accessing Parent Values from Subcharts

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

## Library Charts

### Creating a library chart

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

### Using library chart

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
