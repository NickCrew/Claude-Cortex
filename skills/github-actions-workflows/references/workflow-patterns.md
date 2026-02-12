# GitHub Actions Workflow Patterns

## Matrix Builds

### Multi-OS / Multi-Version Matrix
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node: [18, 20, 22]
    exclude:
      - os: windows-latest
        node: 18
  fail-fast: false
```

### Dynamic Matrix from JSON
```yaml
jobs:
  generate:
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: echo "matrix=$(cat matrix.json)" >> $GITHUB_OUTPUT

  build:
    needs: generate
    strategy:
      matrix: ${{ fromJson(needs.generate.outputs.matrix) }}
```

## Reusable Workflows

### Caller Workflow
```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy-reusable.yml
    with:
      environment: production
      version: ${{ github.sha }}
    secrets: inherit
```

### Reusable Workflow Definition
```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      version:
        required: true
        type: string
    secrets:
      DEPLOY_TOKEN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.version }}
```

### Composite Actions
```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install dependencies and build
inputs:
  node-version:
    default: '20'
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - run: npm ci
      shell: bash
    - run: npm run build
      shell: bash
```

## Secrets Management

### Environment-Scoped Secrets
```yaml
jobs:
  deploy:
    environment: production
    steps:
      - run: deploy --token ${{ secrets.DEPLOY_TOKEN }}
```

### OIDC for Cloud Authentication
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
```

### Best Practices
- Never echo secrets in logs
- Use add-mask for dynamic secrets
- Rotate secrets on a schedule
- Prefer OIDC over long-lived credentials
- Use environment protection rules for sensitive deployments

## Caching Strategies

### Dependency Caching
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Build Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      .next/cache
      dist
    key: build-${{ runner.os }}-${{ hashFiles('src/**', 'package-lock.json') }}
```

### Docker Layer Caching
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Deployment Workflows

### Staged Deployment
```yaml
jobs:
  deploy-staging:
    environment: staging
    steps:
      - run: deploy --env staging

  smoke-test:
    needs: deploy-staging
    steps:
      - run: npm run test:smoke -- --url $STAGING_URL

  deploy-production:
    needs: smoke-test
    environment: production
    steps:
      - run: deploy --env production
```

### Rollback Pattern
```yaml
- name: Deploy
  id: deploy
  run: deploy --version ${{ github.sha }}
  continue-on-error: true

- name: Rollback on failure
  if: steps.deploy.outcome == 'failure'
  run: deploy --version ${{ env.PREVIOUS_VERSION }}
```

## Conditional Execution

### Path-Based Triggers
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

### Conditional Jobs
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

## Concurrency Control

### Cancel In-Progress Runs
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Queue Deployments
```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

## Self-Hosted Runners

### Runner Labels
```yaml
jobs:
  gpu-test:
    runs-on: [self-hosted, linux, gpu]
```

### Security
- Use runner groups for organization-level access control
- Restrict self-hosted runners to private repositories
- Use ephemeral runners for sensitive workloads
- Clean workspace between runs

## Workflow Optimization

### Parallel Jobs
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    runs-on: ubuntu-latest
  build:
    runs-on: ubuntu-latest

  deploy:
    needs: [lint, test, build]
```

### Timeout Limits
```yaml
jobs:
  test:
    timeout-minutes: 30
    steps:
      - run: npm test
        timeout-minutes: 10
```

### Shallow Checkout
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1
    sparse-checkout: |
      src
      tests
```

## Error Handling

### Notifications
```yaml
- name: Notify on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "Build failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}

- name: Always cleanup
  if: always()
  run: cleanup-resources.sh
```
