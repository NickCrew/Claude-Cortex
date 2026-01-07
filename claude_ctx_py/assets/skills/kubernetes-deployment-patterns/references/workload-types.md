# Workload Types

## Deployment (Stateless Applications)

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

## StatefulSet (Stateful Applications)

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

## DaemonSet (Node-Level Services)

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

## Job (One-Time Tasks)

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

## CronJob (Scheduled Tasks)

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
