# Reference: Testing Patterns

## Chart Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
  - name: wget
    image: busybox:latest
    command: ['wget']
    args: ['{{ include "my-app.fullname" . }}:{{ .Values.service.port }}']
```

```yaml
# templates/tests/test-authentication.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-auth"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
  - name: test
    image: curlimages/curl:latest
    command:
      - sh
      - -c
      - |
        TOKEN=$(curl -s -X POST {{ include "my-app.fullname" . }}/auth/token -d '{"user":"test"}' | jq -r .token)
        curl -f -H "Authorization: Bearer $TOKEN" {{ include "my-app.fullname" . }}/api/protected
```

## Running Tests

```bash
# Install and run tests
helm install my-app ./my-app
helm test my-app

# Show test logs
helm test my-app --logs

# Cleanup after tests
helm test my-app --cleanup
```

## Template Linting and Validation

```bash
# Lint chart for issues
helm lint ./my-app

# Lint with custom values
helm lint ./my-app -f values-production.yaml

# Template rendering (dry-run)
helm template my-app ./my-app

# Template with specific values
helm template my-app ./my-app \
  --set replicaCount=5 \
  -f values-production.yaml

# Validate against cluster
helm install my-app ./my-app --dry-run --debug

# Schema validation
helm lint ./my-app --strict
```
