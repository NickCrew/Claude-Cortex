# Reference: Values File Patterns

## Hierarchical Values Organization

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

# Network Policy
networkPolicy:
  enabled: false
  policyTypes:
    - Ingress
    - Egress
  ingress: []
  egress: []
```

## Environment-Specific Values

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

## Values Schema Validation

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
