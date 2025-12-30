# Reference: Hooks and Lifecycle Management

## Hook Types

### Pre-install hook (database migration)

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

### Post-install hook (smoke tests)

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

### Pre-delete hook (backup)

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

## Available Hooks

- `pre-install`, `post-install`
- `pre-delete`, `post-delete`
- `pre-upgrade`, `post-upgrade`
- `pre-rollback`, `post-rollback`
- `test` (run with `helm test`)

## Hook Weights

Control execution order: -2147483648 to 2147483647 (lower first)

## Deletion Policies

- `before-hook-creation`: Delete previous hook before new one
- `hook-succeeded`: Delete after successful execution
- `hook-failed`: Delete if hook fails
