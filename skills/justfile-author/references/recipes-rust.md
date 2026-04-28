# Rust recipe block

Use this when `Cargo.toml` exists at the repo root.

## Standard recipes

### install

Cargo fetches deps on first build. Use `install` to warm the cache:

```just
install:
    cargo fetch
```

### dev / svc-dev

For binaries:

```just
dev:
    cargo run

# If multiple [[bin]] targets exist, take the one that matches the project slug
# or name it explicitly:
# dev:
#     cargo run --bin {{ project }}
```

For services that need fast feedback, prefer `cargo watch` (install with
`cargo install cargo-watch` — the recipe assumes it's available; mention
this in a comment if it is not yet installed):

```just
dev-watch:
    cargo watch -x run
```

### build

```just
build:
    cargo build --release
```

### typecheck

```just
typecheck:
    cargo check --all-targets --all-features
```

### lint

```just
lint:
    cargo clippy --all-targets --all-features -- -D warnings
```

### fmt

Rust projects almost always want a fmt recipe:

```just
fmt:
    cargo fmt --all

fmt-check:
    cargo fmt --all -- --check
```

Add `fmt-check` to the `ci` recipe deps:

```just
ci: fmt-check typecheck lint test
```

### test / test-file / test-watch

```just
test:
    cargo test --all-features

# Run a single test by name path, e.g. `just test-file mymod::tests::it_works`
test-file filter:
    cargo test --all-features {{ filter }}

test-watch:
    cargo watch -x test
```

### clean

```just
clean:
    cargo clean
```

## Workspaces

If `Cargo.toml` has `[workspace]`, prefer `--workspace` on commands that
should run across all members:

```just
build:
    cargo build --workspace --release

test:
    cargo test --workspace --all-features
```

For workspace member-specific recipes, parameterize:

```just
test-crate crate:
    cargo test -p {{ crate }} --all-features
```

## Service patterns

Most Rust services are a single binary, so `svc-dev` typically maps to one
window. For multi-binary workspaces (e.g., a server + a worker), emit
parallel `svc-server` and `svc-worker` recipes calling `cargo run --bin
<name>` via the wrapper.

The `tx-start-<role>.sh` wrapper for Rust usually does NOT need any runtime
activation block — `rust-toolchain.toml` is honored automatically by cargo.
