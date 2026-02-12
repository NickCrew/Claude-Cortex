# Build Systems

## Compilation Optimization

### Incremental Compilation

Only recompile files that have changed or depend on changed files:

```json
// tsconfig.json - enable incremental TypeScript compilation
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo",
    "composite": true
  }
}
```

**Key principle:** Track file hashes and dependency edges. If a file's hash is unchanged and none of its dependencies changed, skip recompilation.

### Parallel Processing

Use all available CPU cores during compilation:

```javascript
// webpack.config.js - parallel loaders
module.exports = {
  module: {
    rules: [{
      test: /\.tsx?$/,
      use: [
        {
          loader: 'thread-loader',
          options: { workers: require('os').cpus().length - 1 }
        },
        'ts-loader'
      ]
    }]
  }
};
```

```bash
# esbuild - inherently parallel
esbuild src/index.ts --bundle --outdir=dist --minify

# tsc with project references for parallel compilation
tsc --build --verbose  # builds projects in dependency order, parallelizes independent ones
```

### Module Resolution Optimization

Reduce the cost of finding modules:

```javascript
// webpack.config.js
module.exports = {
  resolve: {
    // limit search paths
    modules: [path.resolve('./src'), 'node_modules'],
    // specify extensions to try (avoid unnecessary file system calls)
    extensions: ['.ts', '.tsx', '.js'],
    // use package.json "exports" field
    conditionNames: ['import', 'module', 'default'],
    // alias to avoid deep resolution
    alias: { '@': path.resolve('./src') }
  }
};
```

### Type Checking Optimization

Separate type checking from compilation:

```bash
# compile with esbuild (fast, no type checking)
esbuild src/index.ts --bundle --outdir=dist

# type check separately (can run in parallel)
tsc --noEmit --incremental
```

### Dead Code Elimination

```javascript
// webpack production config
module.exports = {
  mode: 'production',  // enables tree shaking
  optimization: {
    usedExports: true,      // mark unused exports
    minimize: true,          // remove dead code
    sideEffects: true,       // respect package.json sideEffects field
    concatenateModules: true // scope hoisting
  }
};
```

---

## Caching Strategies

### Local Filesystem Cache

```javascript
// webpack 5 persistent cache
module.exports = {
  cache: {
    type: 'filesystem',
    buildDependencies: {
      config: [__filename],   // invalidate when config changes
    },
    cacheDirectory: path.resolve('.cache/webpack'),
    compression: 'gzip',
  }
};
```

```bash
# Vite - uses filesystem cache by default
# Cache stored in node_modules/.vite
```

### Remote Cache

Share build artifacts across CI runs and developers:

```json
// turbo.json - Turborepo remote cache
{
  "remoteCache": {
    "enabled": true
  }
}
```

```bash
# Turborepo remote cache setup
npx turbo login
npx turbo link

# Nx remote cache
nx connect-to-nx-cloud
```

### Distributed Cache

```yaml
# Bazel remote cache configuration
build --remote_cache=grpcs://cache.example.com
build --remote_upload_local_results=true
build --remote_timeout=30
```

### Content-Based Hashing

Hash inputs to determine if outputs can be reused:

```
Input hash = hash(source files + config + dependency versions + environment)
If cache[input_hash] exists → reuse cached output
Else → build and store result in cache[input_hash]
```

### Cache Invalidation Rules

| Change Type | Invalidation Scope |
| --- | --- |
| Source file modified | That file + downstream dependents |
| Config file changed | Full rebuild for affected scope |
| Dependency version bumped | Modules importing that dependency |
| Node.js version changed | Full rebuild |
| Environment variable changed | Tasks using that variable |

---

## Incremental Build Patterns

### File Watching

```javascript
// webpack watch mode
module.exports = {
  watch: true,
  watchOptions: {
    ignored: /node_modules/,
    aggregateTimeout: 200,   // batch changes within 200ms
    poll: false              // use native file system events
  }
};
```

### Hot Module Replacement (HMR)

Replace modules in a running application without full reload:

```javascript
// Vite HMR - built in
// vite.config.ts
export default defineConfig({
  server: {
    hmr: {
      overlay: true  // show errors as overlay
    }
  }
});
```

### Affected Detection in Monorepos

Only rebuild packages affected by changes:

```bash
# Turborepo - run only affected tasks
turbo run build --filter=...[HEAD~1]

# Nx - affected detection
nx affected --target=build --base=main --head=HEAD

# Bazel - query affected targets
bazel query "rdeps(//..., set($(git diff --name-only HEAD~1)))"
```

---

## Parallel Execution

### Task-Level Parallelism

```json
// turbo.json - define task dependencies for parallel execution
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    }
  }
}
```

With this config, `lint` runs in parallel with `build` since they have no dependency. `test` waits for `build`.

### Process-Level Parallelism

```bash
# npm-run-all for parallel scripts
npx npm-run-all --parallel lint typecheck test:unit

# GNU parallel for arbitrary commands
find packages -name "package.json" -maxdepth 2 | parallel "cd {//} && npm run build"
```

---

## Dependency Management

### Lock Files

Always commit lock files for reproducible builds:

| Package Manager | Lock File |
| --- | --- |
| npm | package-lock.json |
| yarn | yarn.lock |
| pnpm | pnpm-lock.yaml |
| bun | bun.lock |

### Dependency Deduplication

```bash
# npm - dedupe nested dependencies
npm dedupe

# yarn - dedupe
yarn dedupe

# pnpm - strict by default (hoisting disabled)
# uses content-addressable storage to share dependencies
```

### Phantom Dependencies

In monorepos, prevent packages from importing undeclared dependencies:

```yaml
# .npmrc for pnpm strict mode
strict-peer-dependencies=true
auto-install-peers=false
```

---

## Build Reproducibility

### Deterministic Builds

```javascript
// webpack - consistent output ordering
module.exports = {
  optimization: {
    moduleIds: 'deterministic',    // stable module IDs
    chunkIds: 'deterministic',     // stable chunk IDs
  },
  output: {
    hashFunction: 'xxhash64',     // fast, deterministic hashing
  }
};
```

### Environment Isolation

```dockerfile
# Dockerfile for reproducible builds
FROM node:20-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts   # deterministic install
COPY . .
RUN npm run build
```

---

## CI/CD Pipeline Optimization

### Dependency Caching in CI

```yaml
# GitHub Actions - cache node_modules
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      node_modules
      .cache
    key: deps-${{ hashFiles('package-lock.json') }}
    restore-keys: deps-
```

### Parallel CI Jobs

```yaml
# GitHub Actions - parallel test matrix
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npm test -- --shard=${{ matrix.shard }}/4
```

### Build Artifact Management

```yaml
# upload build artifacts for downstream jobs
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7

# download in deployment job
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```

### Pipeline Speed Tips

1. **Cache aggressively**: Dependencies, build outputs, test fixtures
2. **Run independent jobs in parallel**: Lint, typecheck, and unit tests don't depend on each other
3. **Use sharding**: Split test suites across multiple runners
4. **Skip unnecessary work**: Use path filters to skip unchanged packages
5. **Use faster runners**: Self-hosted runners with SSDs and more cores
6. **Minimize Docker layers**: Order Dockerfile commands by change frequency

---

## Artifact Management

### Content-Addressed Storage

```bash
# store artifacts by content hash
HASH=$(sha256sum dist/bundle.js | cut -d' ' -f1)
aws s3 cp dist/bundle.js s3://artifacts/${HASH}/bundle.js

# retrieve by hash
aws s3 cp s3://artifacts/${HASH}/bundle.js dist/bundle.js
```

### Bundle Analysis

```bash
# webpack bundle analyzer
npx webpack-bundle-analyzer dist/stats.json

# source-map-explorer for any bundler
npx source-map-explorer dist/bundle.js

# Vite bundle analysis
npx vite-bundle-visualizer
```

Track bundle size in CI to prevent regressions:

```bash
# bundlesize - fail CI if bundle exceeds threshold
npx bundlesize --max-size 250kB --files dist/main.*.js
```
