---
name: kubernetes-deployment-patterns
description: Kubernetes deployment strategies and workload patterns for production-grade applications. Use when deploying to Kubernetes, implementing rollout strategies, or designing cloud-native application architectures.
---

# Kubernetes Deployment Patterns

Expert guidance for production-grade Kubernetes deployments covering deployment strategies, workload types, configuration management, resource optimization, and autoscaling patterns for cloud-native applications.

## When to Use This Skill

- Implementing deployment strategies (rolling updates, blue-green, canary releases)
- Choosing appropriate workload types (Deployment, StatefulSet, DaemonSet, Job)
- Designing rollout strategies for zero-downtime deployments
- Implementing configuration management with ConfigMaps and Secrets
- Setting up resource management and autoscaling (HPA, VPA)
- Configuring health checks and probe strategies
- Designing highly available applications on Kubernetes
- Implementing batch processing and scheduled jobs

## Deployment Strategies

### 1. Rolling Update (Default)

**Pattern:** Gradually replace old pods with new ones

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max 2 extra pods during update
      maxUnavailable: 1  # Max 1 pod can be unavailable
  template:
    spec:
      containers:
      - name: app
        image: myapp:v2
```

**Characteristics:**
- Zero downtime for stateless applications
- Gradual traffic shift from old to new version
- Easy rollback with `kubectl rollout undo`
- Both versions run simultaneously during update

**Best for:** Standard web applications, microservices, stateless workloads

**Configuration guidelines:**
```yaml
# Zero-downtime (conservative)
rollingUpdate:
  maxSurge: 1
  maxUnavailable: 0

# Fast rollout (acceptable brief impact)
rollingUpdate:
  maxSurge: 50%
  maxUnavailable: 25%

# Gradual rollout (large deployments)
rollingUpdate:
  maxSurge: 1
  maxUnavailable: 1
```

### 2. Recreate Strategy

**Pattern:** Terminate all old pods before creating new ones

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  strategy:
    type: Recreate
  template:
    spec:
      containers:
      - name: app
        image: myapp:v2
```

**Characteristics:**
- Brief downtime during deployment
- Only one version runs at a time
- Useful when old/new versions cannot coexist
- Faster than rolling updates for compatible workloads

**Best for:** Legacy applications, database schema migrations, resource-constrained environments

**Use cases:**
- Applications requiring exclusive resource access
- Database migrations that change schema
- When running multiple versions causes conflicts
- Development/testing environments where downtime is acceptable

### 3. Blue-Green Deployment

**Pattern:** Run two identical environments, switch traffic between them

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
  labels:
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1
---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
  labels:
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:v2
---
# Service - switch traffic by changing selector
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    app: myapp
    version: blue  # Change to 'green' to switch traffic
  ports:
  - port: 80
    targetPort: 8080
```

**Characteristics:**
- Instant traffic switch
- Full rollback capability
- Requires 2x resources during deployment
- Can test green environment before switching

**Best for:** Mission-critical applications, large-scale deployments, compliance requirements

**Switching process:**
```bash
# 1. Deploy green environment
kubectl apply -f deployment-green.yaml

# 2. Test green environment
kubectl port-forward deployment/app-green 8080:8080

# 3. Switch service to green
kubectl patch service app -p '{"spec":{"selector":{"version":"green"}}}'

# 4. Rollback if needed
kubectl patch service app -p '{"spec":{"selector":{"version":"blue"}}}'

# 5. Delete blue after validation
kubectl delete deployment app-blue
```

### 4. Canary Deployment

**Pattern:** Gradually shift traffic to new version while monitoring

```yaml
# Stable deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
        version: v1
    spec:
      containers:
      - name: app
        image: myapp:v1
---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
        version: v2
    spec:
      containers:
      - name: app
        image: myapp:v2
---
# Service routes to both (proportional to replicas)
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    app: myapp  # Matches both stable and canary
  ports:
  - port: 80
    targetPort: 8080
```

**Traffic distribution:**
- Traffic split based on replica ratios
- Example: 9 stable + 1 canary = 10% canary traffic
- Gradually increase canary replicas
- Monitor metrics before full rollout

**Best for:** High-risk deployments, A/B testing, gradual feature rollouts

**Progressive rollout:**
```bash
# Phase 1: 10% traffic
kubectl scale deployment app-canary --replicas=1  # 1/(9+1) = 10%

# Phase 2: 25% traffic (monitor metrics)
kubectl scale deployment app-canary --replicas=3  # 3/(9+3) = 25%

# Phase 3: 50% traffic (continue monitoring)
kubectl scale deployment app-canary --replicas=9  # 9/(9+9) = 50%

# Phase 4: Full rollout
kubectl scale deployment app-canary --replicas=9
kubectl scale deployment app-stable --replicas=0
kubectl delete deployment app-stable
```

**Advanced canary with Istio/Linkerd:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app
spec:
  hosts:
  - app
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*Chrome.*"
    route:
    - destination:
        host: app
        subset: canary
      weight: 100
  - route:
    - destination:
        host: app
        subset: stable
      weight: 90
    - destination:
        host: app
        subset: canary
      weight: 10
```

## Workload Types

### Deployment (Stateless Applications)

**Use for:** Web servers, APIs, microservices, stateless workers

**Characteristics:**
- Pods are interchangeable
- No persistent identity
- Scale up/down freely
- Rolling updates supported

**Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api
    spec:
      containers:
      - name: api
        image: api:1.0.0
        ports:
        - containerPort: 8080
```

### StatefulSet (Stateful Applications)

**Use for:** Databases, message queues, distributed systems requiring stable identity

**Characteristics:**
- Stable, unique network identifiers
- Stable, persistent storage
- Ordered, graceful deployment and scaling
- Ordered, automated rolling updates

**Example:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: data
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

**StatefulSet features:**
- Pods named: `mongodb-0`, `mongodb-1`, `mongodb-2`
- Predictable DNS: `mongodb-0.mongodb.namespace.svc.cluster.local`
- Persistent storage follows pod identity
- Ordered startup: 0 → 1 → 2
- Ordered shutdown: 2 → 1 → 0

**Headless Service (required):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  clusterIP: None  # Headless
  selector:
    app: mongodb
  ports:
  - port: 27017
```

### DaemonSet (Node-Level Services)

**Use for:** Log collectors, monitoring agents, node-level storage, network plugins

**Characteristics:**
- One pod per node (or selected nodes)
- Automatically scales with cluster
- Runs before other pods (priority)
- Useful for infrastructure components

**Example:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-collector
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: log-collector
  template:
    metadata:
      labels:
        app: log-collector
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.16
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: containers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: containers
        hostPath:
          path: /var/lib/docker/containers
```

**Node selection:**
```yaml
# Run on specific nodes only
spec:
  template:
    spec:
      nodeSelector:
        logging: enabled
      # Or use affinity for more complex selection
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: Exists
```

### Job (One-Time Tasks)

**Use for:** Batch processing, data migration, backup operations, ETL jobs

**Characteristics:**
- Runs until completion
- Retries on failure
- Can run multiple pods in parallel
- Pods not restarted after success

**Example:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
spec:
  completions: 1      # Total successful completions needed
  parallelism: 1      # Pods to run simultaneously
  backoffLimit: 3     # Max retries before marking failed
  activeDeadlineSeconds: 3600  # Job timeout (1 hour)
  template:
    spec:
      restartPolicy: OnFailure  # Required for Jobs
      containers:
      - name: migrator
        image: migration-tool:1.0
        env:
        - name: SOURCE_DB
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: source
        - name: TARGET_DB
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: target
```

**Parallel processing pattern:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-processor
spec:
  completions: 10     # Need 10 successful completions
  parallelism: 3      # Run 3 at a time
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: processor
        image: processor:1.0
        env:
        - name: TASK_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

### CronJob (Scheduled Tasks)

**Use for:** Periodic backups, scheduled reports, cleanup jobs, health checks

**Characteristics:**
- Runs on schedule (cron syntax)
- Creates Jobs on schedule
- Manages Job lifecycle
- Configurable history retention

**Example:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-database
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM UTC
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid  # Don't allow overlapping runs
  startingDeadlineSeconds: 300  # Start within 5 minutes or skip
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:1.0
            env:
            - name: BACKUP_TIMESTAMP
              value: "$(date +%Y%m%d-%H%M%S)"
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

**Cron schedule syntax:**
```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
# │ │ │ │ │
# * * * * *

"0 */6 * * *"      # Every 6 hours
"0 2 * * *"        # Daily at 2 AM
"0 0 * * 0"        # Weekly on Sunday at midnight
"0 0 1 * *"        # Monthly on the 1st at midnight
"*/15 * * * *"     # Every 15 minutes
```

**Concurrency policies:**
- `Allow`: Allow multiple jobs to run (default)
- `Forbid`: Skip new job if previous still running
- `Replace`: Cancel running job and start new one

## Configuration Management

### ConfigMaps

**Use for:** Non-sensitive configuration, application settings, config files

**As environment variables:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: production
  LOG_LEVEL: info
  MAX_CONNECTIONS: "100"
  CACHE_TTL: "3600"
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        envFrom:
        - configMapRef:
            name: app-config
        # Or individual keys
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
```

**As mounted files:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-files
data:
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://backend:8080;
      }
    }
  app.properties: |
    server.port=8080
    logging.level=INFO
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        volumeMounts:
        - name: config
          mountPath: /etc/config
      volumes:
      - name: config
        configMap:
          name: app-config-files
```

**Update strategies:**
```yaml
# ConfigMaps mounted as volumes update automatically
# Env vars do NOT update - need pod restart

# Pattern 1: Version ConfigMaps for env vars
metadata:
  name: app-config-v2  # Increment version

# Pattern 2: Rolling restart after ConfigMap update
kubectl rollout restart deployment/app
```

### Secrets

**Use for:** Passwords, API keys, certificates, tokens

**Creating secrets:**
```bash
# From literal values
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secret123

# From files
kubectl create secret generic tls-cert \
  --from-file=tls.crt=./server.crt \
  --from-file=tls.key=./server.key

# From environment file
kubectl create secret generic app-secrets \
  --from-env-file=./secrets.env
```

**Using secrets:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  username: admin
  password: supersecret
  connection-string: "postgresql://admin:supersecret@db:5432/myapp"
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        # Or mount as files
        volumeMounts:
        - name: db-creds
          mountPath: /etc/secrets
          readOnly: true
      volumes:
      - name: db-creds
        secret:
          secretName: db-credentials
          defaultMode: 0400  # Read-only for owner
```

**Security best practices:**
- Never commit secrets to Git
- Use external secret management (Sealed Secrets, External Secrets Operator, Vault)
- Enable encryption at rest for etcd
- Use RBAC to limit secret access
- Rotate secrets regularly
- Consider using workload identity for cloud credentials

## Resource Management & Autoscaling

### Resource Requests and Limits

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

**Resource units:**
- CPU: `1` = 1 core, `500m` = 0.5 cores, `100m` = 0.1 cores
- Memory: `128Mi` (mebibytes), `1Gi` (gibibytes), `500M` (megabytes)

**QoS classes (auto-assigned):**
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

### Horizontal Pod Autoscaler (HPA)

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

### Vertical Pod Autoscaler (VPA)

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

### LimitRange (Namespace Defaults)

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

### ResourceQuota (Namespace Limits)

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

## Best Practices Summary

### Deployment Strategy Selection

| Strategy | Zero-Downtime | Resource Cost | Rollback Speed | Use Case |
|----------|--------------|---------------|----------------|----------|
| Rolling Update | Yes | 1x + surge | Fast | Standard deployments |
| Recreate | No | 1x | Fast | Dev/test, incompatible versions |
| Blue-Green | Yes | 2x | Instant | Mission-critical, compliance |
| Canary | Yes | 1x + canary | Progressive | High-risk changes, A/B testing |

### Production Checklist

**Deployment configuration:**
- [ ] Set appropriate replica count (≥3 for HA)
- [ ] Configure update strategy for zero-downtime
- [ ] Implement pod disruption budgets
- [ ] Set pod anti-affinity for spread across nodes/zones
- [ ] Configure topology spread constraints

**Resource management:**
- [ ] Set resource requests and limits
- [ ] Configure HPA for automatic scaling
- [ ] Consider VPA for right-sizing
- [ ] Implement namespace quotas
- [ ] Monitor resource usage and adjust

**Configuration:**
- [ ] Use ConfigMaps for configuration
- [ ] Store secrets in Secret manager or external vault
- [ ] Version ConfigMaps for env vars
- [ ] Mount secrets as files, not env vars (when possible)

**Health and monitoring:**
- [ ] Implement liveness probes
- [ ] Implement readiness probes
- [ ] Add startup probes for slow-starting apps
- [ ] Configure appropriate probe timing
- [ ] Export metrics for monitoring

**Security:**
- [ ] Run as non-root user
- [ ] Use read-only root filesystem
- [ ] Drop all capabilities
- [ ] Enable seccomp profile
- [ ] Implement Pod Security Standards

### Anti-Patterns to Avoid

1. **Latest tag:** Always use specific version tags
2. **No resource limits:** Causes resource starvation
3. **No health checks:** Kubernetes can't manage pod health
4. **Secrets in ConfigMaps:** Use Secrets for sensitive data
5. **Single replica in production:** No high availability
6. **No update strategy:** Unpredictable deployment behavior
7. **Privileged containers:** Security vulnerability
8. **HostPath volumes:** Not portable, security risk
9. **No monitoring:** Can't detect issues
10. **Manual scaling:** Use HPA for automatic scaling

## Resources

- **Official Docs:** https://kubernetes.io/docs/concepts/workloads/
- **Deployment Strategies:** https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- **StatefulSets:** https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- **Autoscaling:** https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- **Configuration:** https://kubernetes.io/docs/concepts/configuration/
- **Best Practices:** https://kubernetes.io/docs/concepts/configuration/overview/
