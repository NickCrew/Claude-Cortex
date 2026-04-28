# Go recipe block

Use this when `go.mod` exists at the repo root.

## Standard recipes

### install

Go fetches deps on first build. Use `install` to warm the module cache:

```just
install:
    go mod download
```

### dev / svc-dev

For a single-main project:

```just
dev:
    go run .
```

For repos with `cmd/<name>/main.go` layout:

```just
dev:
    go run ./cmd/{{ project }}
```

For fast iteration, prefer `air` (a hot reloader) if `.air.toml` exists or
the team standardizes on it:

```just
dev-watch:
    air
```

### build

```just
build:
    go build -o bin/{{ project }} ./cmd/{{ project }}
```

For multi-binary repos:

```just
build:
    go build -o bin/ ./cmd/...
```

### typecheck

Go's compiler is the typechecker. `go vet` is the closest analog to a
separate static-check pass:

```just
typecheck:
    go vet ./...
```

### lint

If `.golangci.yml` exists:

```just
lint:
    golangci-lint run
```

Otherwise, leave lint as `go vet` (already covered by typecheck) and skip
the standalone `lint` recipe.

### fmt

```just
fmt:
    go fmt ./...

fmt-check:
    @if [ -n "$(gofmt -l .)" ]; then echo "Files need formatting:"; gofmt -l .; exit 1; fi
```

### test / test-file / test-watch

```just
test:
    go test ./...

# Run tests in a single package: `just test-file ./internal/foo`
test-file pkg:
    go test {{ pkg }}

test-race:
    go test -race ./...

test-cover:
    go test -coverprofile=coverage.out ./...
    go tool cover -html=coverage.out -o coverage.html
```

There is no native watch mode; if needed, document `gotestsum --watch` or
`reflex` rather than baking it in.

### clean

```just
clean:
    rm -rf bin coverage.out coverage.html
    go clean -cache
```

## Service patterns

Most Go services are a single `main` package. The `tx-start-<role>.sh`
wrapper for Go projects usually needs no runtime activation — `go.mod` and
the system Go install handle it. The wrapper exists primarily for env-var
defaults (PORT, DATABASE_URL, etc.).
