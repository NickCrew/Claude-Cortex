# Configuration Management

## ConfigMaps

**Use for:** Non-sensitive configuration, application settings, config files

### As Environment Variables

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

### As Mounted Files

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

### Update Strategies

```yaml
# ConfigMaps mounted as volumes update automatically
# Env vars do NOT update - need pod restart

# Pattern 1: Version ConfigMaps for env vars
metadata:
  name: app-config-v2  # Increment version

# Pattern 2: Rolling restart after ConfigMap update
kubectl rollout restart deployment/app
```

## Secrets

**Use for:** Passwords, API keys, certificates, tokens

### Creating Secrets

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

### Using Secrets

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

### Security Best Practices

- Never commit secrets to Git
- Use external secret management (Sealed Secrets, External Secrets Operator, Vault)
- Enable encryption at rest for etcd
- Use RBAC to limit secret access
- Rotate secrets regularly
- Consider using workload identity for cloud credentials
