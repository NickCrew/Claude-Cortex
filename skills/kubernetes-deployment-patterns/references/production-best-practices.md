# Production Best Practices

## Deployment Configuration

- [ ] Set appropriate replica count (≥3 for HA)
- [ ] Configure update strategy for zero-downtime
- [ ] Implement pod disruption budgets
- [ ] Set pod anti-affinity for spread across nodes/zones
- [ ] Configure topology spread constraints

## Resource Management

- [ ] Set resource requests and limits
- [ ] Configure HPA for automatic scaling
- [ ] Consider VPA for right-sizing
- [ ] Implement namespace quotas
- [ ] Monitor resource usage and adjust

## Configuration

- [ ] Use ConfigMaps for configuration
- [ ] Store secrets in Secret manager or external vault
- [ ] Version ConfigMaps for env vars
- [ ] Mount secrets as files, not env vars (when possible)

## Health and Monitoring

- [ ] Implement liveness probes
- [ ] Implement readiness probes
- [ ] Add startup probes for slow-starting apps
- [ ] Configure appropriate probe timing
- [ ] Export metrics for monitoring

## Security

- [ ] Run as non-root user
- [ ] Use read-only root filesystem
- [ ] Drop all capabilities
- [ ] Enable seccomp profile
- [ ] Implement Pod Security Standards

## Anti-Patterns to Avoid

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

## High Availability Patterns

### Multi-Replica Deployments

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: myapp
              topologyKey: kubernetes.io/hostname
```

### Pod Disruption Budgets

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

### Topology Spread Constraints

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: myapp
```

## Health Check Patterns

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

### Startup Probe (for slow-starting apps)

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 30  # 30 * 10 = 300s max startup time
```

## Security Hardening

### Non-Root User

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
```

### Read-Only Root Filesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
  allowPrivilegeEscalation: false
```

### Security Context Complete Example

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
```
