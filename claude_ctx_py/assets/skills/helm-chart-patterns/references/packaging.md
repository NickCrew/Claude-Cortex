# Reference: Packaging and Distribution

## Packaging Charts

```bash
# Package chart
helm package ./my-app

# Package with specific version
helm package ./my-app --version 1.2.3

# Package with dependency update
helm package ./my-app --dependency-update

# Sign package
helm package ./my-app --sign --key 'my-key' --keyring ~/.gnupg/secring.gpg
```

## Chart Repositories

### Creating repository index

```bash
# Create index.yaml
helm repo index . --url https://charts.example.com

# Update existing index
helm repo index . --url https://charts.example.com --merge index.yaml
```

### index.yaml structure

```yaml
apiVersion: v1
entries:
  my-app:
  - apiVersion: v2
    appVersion: "2.5.0"
    created: "2024-01-01T00:00:00Z"
    description: Production-ready web application chart
    digest: sha256:abcd1234...
    name: my-app
    urls:
    - https://charts.example.com/my-app-1.2.3.tgz
    version: 1.2.3
```

### Using repositories

```bash
# Add repository
helm repo add myrepo https://charts.example.com

# Update repository cache
helm repo update

# Search repository
helm repo search myrepo/

# Install from repository
helm install my-app myrepo/my-app --version 1.2.3
```

## OCI Registry Support

```bash
# Login to OCI registry
helm registry login registry.example.com

# Package and push
helm package ./my-app
helm push my-app-1.2.3.tgz oci://registry.example.com/charts

# Install from OCI
helm install my-app oci://registry.example.com/charts/my-app --version 1.2.3

# Pull chart
helm pull oci://registry.example.com/charts/my-app --version 1.2.3
```
