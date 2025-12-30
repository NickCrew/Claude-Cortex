# Reference: Template Patterns

## Helper Templates (_helpers.tpl)

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

## Conditionals and Flow Control

### Conditional resource creation

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

### Multiple conditions

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

### if-else chains

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

## Loops and Iteration

### Range over lists

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

### Creating multiple resources

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

### Indexed loops

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

## Template Functions

### String manipulation

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

### Encoding and hashing

```yaml
# Base64 encoding
data:
  config: {{ .Values.config | b64enc }}

# SHA256 checksum (for triggering updates)
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

### Type conversion

```yaml
# Defaults and coalesce
value: {{ .Values.custom | default "default-value" }}
value: {{ coalesce .Values.a .Values.b .Values.c "fallback" }}

# Type assertions
replicas: {{ .Values.replicaCount | int }}
enabled: {{ .Values.enabled | ternary "yes" "no" }}
```

### Logical operators

```yaml
{{- if and .Values.enabled (eq .Values.type "web") }}
{{- if or .Values.devMode (eq .Values.env "development") }}
{{- if not .Values.disabled }}
```
