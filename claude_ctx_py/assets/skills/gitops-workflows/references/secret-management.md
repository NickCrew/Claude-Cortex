# Secret Management

## 1. Sealed Secrets

**Install controller:**
```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal
```

**Encrypt secrets:**
```bash
# Create regular secret
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml > secret.yaml

# Encrypt for cluster
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git
git add sealed-secret.yaml
git commit -m "Add encrypted database credentials"
```

**SealedSecret manifest:**
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  encryptedData:
    username: AgBj7V8X...
    password: AgCK9Qw2...
  template:
    metadata:
      name: db-credentials
      namespace: production
    type: Opaque
```

## 2. External Secrets Operator

**Install ESO:**
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

**SecretStore (AWS Secrets Manager):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
```

**ExternalSecret:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore

  target:
    name: db-credentials
    creationPolicy: Owner

  data:
  - secretKey: username
    remoteRef:
      key: production/database/credentials
      property: username
  - secretKey: password
    remoteRef:
      key: production/database/credentials
      property: password
```

**ClusterSecretStore (shared):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
```

## 3. SOPS (Secrets Operations)

**Setup (with age encryption):**
```bash
# Install SOPS
brew install sops

# Install age
brew install age

# Generate age key
age-keygen -o key.txt

# Configure .sops.yaml
cat <<EOF > .sops.yaml
creation_rules:
  - path_regex: .*/production/.*
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
EOF
```

**Encrypt secrets:**
```yaml
# Create secret
cat <<EOF > secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
stringData:
  username: admin
  password: supersecret
EOF

# Encrypt with SOPS
sops --encrypt --in-place secret.yaml

# Commit encrypted file
git add secret.yaml
```

**Flux integration:**
```yaml
# Kustomization with SOPS
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age
  sourceRef:
    kind: GitRepository
    name: gitops-repo
```
