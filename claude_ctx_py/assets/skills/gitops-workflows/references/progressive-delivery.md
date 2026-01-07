# Progressive Delivery

## ArgoCD Rollouts (Canary)

**Rollout resource:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: frontend
spec:
  replicas: 10
  revisionHistoryLimit: 3

  selector:
    matchLabels:
      app: frontend

  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: frontend:v2

  strategy:
    canary:
      steps:
      - setWeight: 10          # 10% traffic to new version
      - pause: {duration: 2m}  # Wait 2 minutes
      - setWeight: 25
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 75
      - pause: {duration: 5m}

      # Automated analysis
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: frontend

      # Traffic routing
      trafficRouting:
        istio:
          virtualService:
            name: frontend
            routes:
            - primary
```

**Analysis template:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name

  metrics:
  - name: success-rate
    interval: 1m
    count: 5
    successCondition: result[0] >= 0.95
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(
            http_requests_total{service="{{args.service-name}}",status!~"5.."}[1m]
          )) /
          sum(rate(
            http_requests_total{service="{{args.service-name}}"}[1m]
          ))
```

## Flagger (Flux Progressive Delivery)

**Install Flagger:**
```bash
kubectl apply -k github.com/fluxcd/flagger//kustomize/istio
```

**Canary resource:**
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: frontend
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend

  service:
    port: 80
    targetPort: 8080

  analysis:
    interval: 1m
    threshold: 5          # Number of iterations
    maxWeight: 50         # Max traffic to canary
    stepWeight: 10        # Traffic increase per iteration

    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m

    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://frontend-canary/"
```
