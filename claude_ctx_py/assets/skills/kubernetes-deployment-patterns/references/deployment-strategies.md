# Deployment Strategies

## 1. Rolling Update (Default)

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

## 2. Recreate Strategy

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

## 3. Blue-Green Deployment

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

## 4. Canary Deployment

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

## Strategy Selection Guide

| Strategy | Zero-Downtime | Resource Cost | Rollback Speed | Use Case |
|----------|--------------|---------------|----------------|----------|
| Rolling Update | Yes | 1x + surge | Fast | Standard deployments |
| Recreate | No | 1x | Fast | Dev/test, incompatible versions |
| Blue-Green | Yes | 2x | Instant | Mission-critical, compliance |
| Canary | Yes | 1x + canary | Progressive | High-risk changes, A/B testing |
