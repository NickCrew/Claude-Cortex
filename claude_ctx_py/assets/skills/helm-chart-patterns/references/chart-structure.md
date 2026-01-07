# Reference: Chart Structure Foundations

## Standard Chart Layout

```
my-app/
├── Chart.yaml              # Chart metadata (required)
├── Chart.lock              # Dependency lock file (generated)
├── values.yaml             # Default configuration (required)
├── values.schema.json      # Values validation schema
├── README.md               # Chart documentation
├── .helmignore             # Packaging exclusions
├── charts/                 # Dependency charts
│   └── postgresql-12.0.0.tgz
├── crds/                   # Custom Resource Definitions
│   └── my-crd.yaml
├── templates/              # K8s manifest templates (required)
│   ├── NOTES.txt          # Post-install instructions
│   ├── _helpers.tpl       # Template functions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── serviceaccount.yaml
│   ├── hpa.yaml
│   └── tests/
│       └── test-connection.yaml
└── files/                  # Static files to include
    └── config/
        └── app.conf
```

## Chart.yaml Configuration

```yaml
apiVersion: v2
name: my-application
version: 1.2.3                    # Chart version (SemVer)
appVersion: "2.5.0"              # Application version
description: Production-ready web application chart
type: application                 # application or library
keywords:
  - web
  - api
  - microservices
home: https://example.com
sources:
  - https://github.com/example/my-app
maintainers:
  - name: Platform Team
    email: platform@example.com
icon: https://example.com/icon.png
kubeVersion: ">=1.24.0-0"        # Compatible K8s versions
dependencies:
  - name: postgresql
    version: "~12.0.0"           # Semver range
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    tags:
      - database
    import-values:
      - child: auth
        parent: postgresql.auth
annotations:
  category: ApplicationServer
  licenses: Apache-2.0
```

## Chart Types

- `application`: Standard deployable charts
- `library`: Reusable template helpers (not installable)

## Version Constraints

- Use SemVer for chart versions
- Use constraints for dependencies:
  - `~1.2.3` (>=1.2.3, <1.3.0)
  - `^1.2.3` (>=1.2.3, <2.0.0)
