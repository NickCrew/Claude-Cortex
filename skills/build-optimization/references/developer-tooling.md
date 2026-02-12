# Developer Tooling

## Plugin System Design

### Hook-Based Architecture

Plugins register callbacks for lifecycle events:

```typescript
interface Plugin {
  name: string;
  setup(hooks: PluginHooks): void;
}

interface PluginHooks {
  beforeBuild: AsyncHook<BuildConfig>;
  afterBuild: AsyncHook<BuildResult>;
  onError: AsyncHook<BuildError>;
  transform: AsyncHook<{ code: string; id: string }>;
}

// example plugin
const timingPlugin: Plugin = {
  name: 'timing',
  setup(hooks) {
    let start: number;
    hooks.beforeBuild.tap(() => { start = Date.now(); });
    hooks.afterBuild.tap((result) => {
      console.log(`Build completed in ${Date.now() - start}ms`);
    });
  }
};
```

### Middleware Pattern

Chain transformations through composable functions:

```typescript
type Middleware = (ctx: Context, next: () => Promise<void>) => Promise<void>;

class Pipeline {
  private middlewares: Middleware[] = [];

  use(fn: Middleware) {
    this.middlewares.push(fn);
    return this;
  }

  async execute(ctx: Context) {
    let index = 0;
    const next = async () => {
      if (index < this.middlewares.length) {
        await this.middlewares[index++](ctx, next);
      }
    };
    await next();
  }
}

// usage
pipeline
  .use(loggingMiddleware)
  .use(cachingMiddleware)
  .use(transformMiddleware);
```

### Plugin API Stability

- Version your plugin API with semver
- Document which hooks are stable vs. experimental
- Provide migration guides when changing hook signatures
- Use TypeScript interfaces to define the plugin contract

---

## Code Generation Patterns

### Template-Based Generation

```typescript
// template-based code generator
import Handlebars from 'handlebars';

const componentTemplate = Handlebars.compile(`
import React from 'react';

interface {{name}}Props {
{{#each props}}
  {{this.name}}: {{this.type}};
{{/each}}
}

export function {{name}}({ {{propNames}} }: {{name}}Props) {
  return (
    <div className="{{kebabCase name}}">
      {/* TODO: implement */}
    </div>
  );
}
`);

function generateComponent(name: string, props: Prop[]) {
  return componentTemplate({
    name,
    props,
    propNames: props.map(p => p.name).join(', '),
  });
}
```

### AST Manipulation

Transform code structurally rather than textually:

```typescript
import * as ts from 'typescript';

function addLogging(sourceFile: ts.SourceFile): ts.SourceFile {
  const transformer: ts.TransformerFactory<ts.SourceFile> = (context) => {
    return (node) => {
      function visit(node: ts.Node): ts.Node {
        if (ts.isFunctionDeclaration(node) && node.name) {
          // inject console.log at the start of every function
          const logStatement = ts.factory.createExpressionStatement(
            ts.factory.createCallExpression(
              ts.factory.createPropertyAccessExpression(
                ts.factory.createIdentifier('console'),
                'log'
              ),
              undefined,
              [ts.factory.createStringLiteral(`Entering ${node.name.text}`)]
            )
          );
          return ts.factory.updateFunctionDeclaration(
            node, node.modifiers, node.asteriskToken, node.name,
            node.typeParameters, node.parameters, node.type,
            ts.factory.createBlock([logStatement, ...node.body!.statements])
          );
        }
        return ts.visitEachChild(node, visit, context);
      }
      return ts.visitNode(node, visit) as ts.SourceFile;
    };
  };
  const result = ts.transform(sourceFile, [transformer]);
  return result.transformed[0];
}
```

### Schema-Driven Generation

Generate code from OpenAPI, GraphQL, or JSON Schema:

```bash
# OpenAPI to TypeScript
npx openapi-typescript api/openapi.yaml -o src/types/api.ts

# GraphQL codegen
npx graphql-codegen --config codegen.yml

# JSON Schema to TypeScript
npx json2ts -i schemas/ -o src/types/
```

### Type Generation

Generate types from runtime data or external sources:

```bash
# Prisma - generate types from database schema
npx prisma generate

# tRPC - infer types from API routes (no generation needed)
# Zod - infer TypeScript types from validation schemas
type User = z.infer<typeof userSchema>;
```

---

## Linting and Formatting Configuration

### ESLint Setup

```javascript
// eslint.config.js (flat config)
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
    }
  },
  {
    ignores: ['dist/', 'node_modules/', 'coverage/'],
  }
);
```

### Prettier Integration

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

```bash
# avoid ESLint and Prettier conflicts
npm install -D eslint-config-prettier

# run both efficiently
npx prettier --check .
npx eslint .
```

### Pre-Commit Hooks

```bash
# install husky + lint-staged
npm install -D husky lint-staged
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

---

## IDE Integration

### VS Code Settings for Build Tools

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "search.exclude": {
    "dist": true,
    "node_modules": true,
    ".cache": true
  }
}
```

### VS Code Tasks

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build",
      "type": "npm",
      "script": "build",
      "group": { "kind": "build", "isDefault": true },
      "problemMatcher": ["$tsc"]
    },
    {
      "label": "Test",
      "type": "npm",
      "script": "test",
      "group": { "kind": "test", "isDefault": true }
    }
  ]
}
```

### Language Server Protocol (LSP)

Key capabilities for custom tools:

- Diagnostics (errors, warnings in editor)
- Completions (autocomplete suggestions)
- Hover information (documentation on hover)
- Go to definition / find references
- Code actions (quick fixes, refactoring)

---

## Task Runner Patterns

### npm Scripts Organization

```json
{
  "scripts": {
    "build": "tsc && vite build",
    "build:watch": "tsc --watch & vite build --watch",
    "dev": "vite",
    "lint": "eslint . && prettier --check .",
    "lint:fix": "eslint --fix . && prettier --write .",
    "test": "vitest",
    "test:ci": "vitest run --coverage",
    "typecheck": "tsc --noEmit",
    "validate": "npm-run-all --parallel lint typecheck test:ci"
  }
}
```

### Makefile for Polyglot Projects

```makefile
.PHONY: build test lint clean

build: node_modules
	npm run build

test: node_modules
	npm run test:ci

lint: node_modules
	npm run lint

clean:
	rm -rf dist node_modules/.cache

node_modules: package-lock.json
	npm ci
	touch node_modules  # update timestamp for make
```

---

## Dependency Update Automation

### Renovate Configuration

```json
// renovate.json
{
  "extends": ["config:base"],
  "schedule": ["before 8am on Monday"],
  "automerge": true,
  "automergeType": "branch",
  "packageRules": [
    {
      "matchUpdateTypes": ["patch", "minor"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["breaking-change"]
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true
    }
  ]
}
```

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    groups:
      dev-dependencies:
        dependency-type: development
        update-types: [minor, patch]
      production-dependencies:
        dependency-type: production
```

---

## Monorepo Tooling

### Turborepo

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

Key features: Remote caching, task parallelism, affected filtering.

### Nx

```json
// nx.json
{
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "cache": true
    },
    "test": {
      "cache": true
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*"],
    "production": ["default", "!{projectRoot}/**/*.spec.*"]
  }
}
```

Key features: Computation caching, affected detection, project graph visualization, code generators.

### Bazel

```python
# BUILD file
load("@npm//:defs.bzl", "npm_link_all_packages")
load("@aspect_rules_ts//ts:defs.bzl", "ts_project")

ts_project(
    name = "lib",
    srcs = glob(["src/**/*.ts"]),
    deps = ["//:node_modules/@types/node"],
    declaration = True,
    tsconfig = ":tsconfig",
)
```

Key features: Hermetic builds, content-addressable cache, distributed execution, language-agnostic.

### Choosing a Monorepo Tool

| Factor | Turborepo | Nx | Bazel |
| --- | --- | --- | --- |
| Setup complexity | Low | Medium | High |
| Caching | Remote cache | Nx Cloud | Remote execution |
| Language support | JS/TS focused | JS/TS + plugins | Any language |
| Affected detection | Git-based | Project graph | Query language |
| Best for | JS/TS monorepos | Enterprise JS/TS | Large polyglot repos |
