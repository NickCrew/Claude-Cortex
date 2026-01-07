# Resource Management & Autoscaling

## Resource Requests and Limits

**Requests:** Guaranteed resources, used for scheduling
**Limits:** Maximum resources, enforced by kubelet

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          requests:
            memory: "256Mi"   # Guaranteed memory
            cpu: "250m"       # Guaranteed CPU (0.25 cores)
          limits:
            memory: "512Mi"   # Max memory (OOMKilled if exceeded)
            cpu: "1000m"      # Max CPU (throttled if exceeded)
```

### Resource Units

- **CPU:** `1` = 1 core, `500m` = 0.5 cores, `100m` = 0.1 cores
- **Memory:** `128Mi` (mebibytes), `1Gi` (gibibytes), `500M` (megabytes)

### QoS Classes (Auto-Assigned)

```yaml
# Guaranteed: requests = limits (highest priority)
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# Burstable: requests < limits (medium priority)
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"

# BestEffort: no requests/limits (lowest priority, first evicted)
resources: {}
```

## Horizontal Pod Autoscaler (HPA)

**Scale based on metrics:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale if avg CPU > 70%
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Scale if avg memory > 80%
  # Custom metrics (requires metrics adapter)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down max 50% at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Can double size at once
        periodSeconds: 30
```

**Requirements:**
- Metrics Server must be installed
- Resource requests must be set
- Target must support scaling (Deployment, StatefulSet, ReplicaSet)

## Vertical Pod Autoscaler (VPA)

**Automatically adjust resource requests/limits:**

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: Auto  # Auto, Recreate, Initial, Off
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 2Gi
      controlledResources: ["cpu", "memory"]
```

**Update modes:**
- `Auto`: VPA updates pods automatically (requires restart)
- `Recreate`: VPA recreates pods to apply updates
- `Initial`: Only set resources on pod creation
- `Off`: Only generate recommendations

**Note:** VPA and HPA should not target the same metrics (CPU/memory). Use VPA for right-sizing, HPA for scaling.

## LimitRange (Namespace Defaults)

**Set default requests/limits per namespace:**

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: resource-limits
  namespace: production
spec:
  limits:
  - max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 250m
      memory: 256Mi
    type: Container
  - max:
      cpu: "4"
      memory: 4Gi
    type: Pod
```

## ResourceQuota (Namespace Limits)

**Limit total resource usage per namespace:**

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "50"
    services: "20"
```
