"""Git worktree management helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import subprocess


@dataclass
class WorktreeInfo:
    """Represents a git worktree entry."""

    path: Path
    head: str
    branch: Optional[str]
    locked: bool
    prunable: bool
    detached: bool
    is_main: bool
    lock_reason: Optional[str] = None
    prune_reason: Optional[str] = None


_WORKTREE_DIR_KEY = "cortex.worktreeDir"


def _run_git(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 127, "", "git not found"
    except OSError as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def _resolve_repo_root(cwd: Path | None = None) -> Tuple[Optional[Path], Optional[str]]:
    base = cwd or Path.cwd()
    code, out, err = _run_git(["rev-parse", "--show-toplevel"], base)
    if code != 0:
        message = (err or out or "Not a git repository").strip()
        return None, message
    root = out.strip()
    if not root:
        return None, "Failed to resolve git root"
    return Path(root), None


def _get_configured_worktree_dir(repo_root: Path) -> Optional[Path]:
    code, out, _err = _run_git(
        ["config", "--local", "--get", _WORKTREE_DIR_KEY], repo_root
    )
    if code != 0:
        return None
    value = out.strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path


def _resolve_base_dir(repo_root: Path) -> Tuple[Path, str]:
    configured = _get_configured_worktree_dir(repo_root)
    if configured:
        return configured, "configured"

    preferred = repo_root / ".worktrees"
    fallback = repo_root / "worktrees"
    if preferred.is_dir():
        return preferred, "auto"
    if fallback.is_dir():
        return fallback, "auto"
    return preferred, "auto"


def _normalize_branch(ref: Optional[str]) -> Optional[str]:
    if not ref:
        return None
    prefix = "refs/heads/"
    if ref.startswith(prefix):
        return ref[len(prefix) :]
    return ref


def _parse_worktree_porcelain(output: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": line[len("worktree ") :].strip()}
            continue

        if " " in line:
            key, value = line.split(" ", 1)
            key = key.strip()
            value = value.strip()
        else:
            key, value = line, ""

        if key in {"bare", "detached", "locked", "prunable"} and not value:
            current[key] = "true"
        else:
            current[key] = value or "true"

    if current:
        entries.append(current)
    return entries


def _build_worktree_info(raw: Dict[str, str], repo_root: Path) -> WorktreeInfo:
    path = Path(raw.get("path", "")).expanduser()
    head = raw.get("HEAD", "")
    branch = _normalize_branch(raw.get("branch"))
    locked = "locked" in raw
    prunable = "prunable" in raw
    detached = "detached" in raw or branch is None
    lock_reason = raw.get("locked") if locked else None
    prune_reason = raw.get("prunable") if prunable else None
    is_main = False
    try:
        is_main = path.resolve() == repo_root.resolve()
    except OSError:
        is_main = False

    return WorktreeInfo(
        path=path,
        head=head,
        branch=branch,
        locked=locked,
        prunable=prunable,
        detached=detached,
        is_main=is_main,
        lock_reason=lock_reason,
        prune_reason=prune_reason,
    )


def worktree_discover(
    cwd: Path | None = None,
) -> Tuple[Optional[Path], List[WorktreeInfo], Optional[str]]:
    """Return (repo_root, worktrees, error_message)."""
    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return None, [], error or "No git repository found"

    code, out, err = _run_git(["worktree", "list", "--porcelain"], repo_root)
    if code != 0:
        message = (err or out or "Failed to list worktrees").strip()
        return repo_root, [], message

    entries = _parse_worktree_porcelain(out)
    worktrees = [_build_worktree_info(entry, repo_root) for entry in entries]
    return repo_root, worktrees, None


def worktree_list(cwd: Path | None = None) -> Tuple[int, str]:
    repo_root, worktrees, error = worktree_discover(cwd)
    if error:
        return 1, error
    if repo_root is None:
        return 1, "No git repository found"

    base_dir, base_source = _resolve_base_dir(repo_root)
    lines: List[str] = [
        f"Worktrees for {repo_root}:",
        f"Base directory ({base_source}): {base_dir}",
    ]
    if not worktrees:
        lines.append("  (none)")
        return 0, "\n".join(lines)

    for entry in worktrees:
        branch = entry.branch or "detached"
        if entry.is_main:
            branch = f"{branch} (main)"
        status_parts: List[str] = []
        if entry.detached:
            status_parts.append("detached")
        if entry.locked:
            status_parts.append("locked")
        if entry.prunable:
            status_parts.append("prunable")
        status = ", ".join(status_parts) if status_parts else "clean"
        head = entry.head[:8] if entry.head else "unknown"

        display_path = entry.path
        try:
            display_path = entry.path.resolve().relative_to(repo_root.resolve())
        except Exception:
            display_path = entry.path

        lines.append(f"  {branch:<20} {head:<8} {status:<12} {display_path}")

    return 0, "\n".join(lines)


def _select_worktree_base(repo_root: Path) -> Path:
    base_dir, _source = _resolve_base_dir(repo_root)
    return base_dir


def worktree_get_base_dir(
    cwd: Path | None = None,
) -> Tuple[Optional[Path], Optional[str], Optional[str]]:
    """Return (base_dir, source, error)."""
    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return None, None, error or "No git repository found"

    base_dir, source = _resolve_base_dir(repo_root)
    return base_dir, source, None


def worktree_set_base_dir(
    base_dir: str,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    if not base_dir or not base_dir.strip():
        return 1, "Base directory is required"

    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return 1, error or "No git repository found"

    raw = Path(base_dir).expanduser()
    if not raw.is_absolute():
        raw = (repo_root / raw).resolve()
    else:
        raw = raw.resolve()

    if raw.exists() and not raw.is_dir():
        return 1, f"{raw} exists and is not a directory"

    try:
        raw.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return 1, f"Failed to create directory: {exc}"

    try:
        rel = raw.relative_to(repo_root.resolve())
        store_value = rel.as_posix()
    except Exception:
        store_value = str(raw)

    code, out, err = _run_git(
        ["config", "--local", _WORKTREE_DIR_KEY, store_value], repo_root
    )
    if code != 0:
        message = (err or out or "Failed to update git config").strip()
        return code, message

    return 0, f"Worktree base directory set to {raw}"


def worktree_clear_base_dir(cwd: Path | None = None) -> Tuple[int, str]:
    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return 1, error or "No git repository found"

    configured = _get_configured_worktree_dir(repo_root)
    if not configured:
        return 0, "No worktree base directory configured"

    code, out, err = _run_git(
        ["config", "--local", "--unset", _WORKTREE_DIR_KEY], repo_root
    )
    if code != 0:
        message = (err or out or "Failed to clear git config").strip()
        return code, message

    return 0, "Cleared worktree base directory"


def _sanitize_branch_path(branch: str) -> Path:
    clean = branch.strip()
    if not clean:
        raise ValueError("Branch name is required")
    if clean.startswith("-"):
        raise ValueError("Branch name cannot start with '-'")
    parts = [p for p in re.split(r"[\\/]+", clean) if p]
    for part in parts:
        if part in {".", ".."}:
            raise ValueError("Branch name contains invalid path segment")
    return Path(*parts)


def worktree_default_path(
    branch: str, cwd: Path | None = None
) -> Tuple[Optional[Path], Optional[str]]:
    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return None, error or "No git repository found"

    try:
        rel = _sanitize_branch_path(branch)
    except ValueError as exc:
        return None, str(exc)

    base_dir = _select_worktree_base(repo_root)
    return base_dir / rel, None


def _git_branch_exists(repo_root: Path, branch: str) -> bool:
    ref = branch
    if not ref.startswith("refs/heads/"):
        ref = f"refs/heads/{branch}"
    code, _out, _err = _run_git(
        ["show-ref", "--verify", "--quiet", ref], repo_root
    )
    return code == 0


def _ensure_gitignore_entry(
    repo_root: Path, entry: str
) -> Tuple[bool, Optional[str]]:
    gitignore_path = repo_root / ".gitignore"
    entry = entry.strip()
    if not entry:
        return False, None
    if not entry.endswith("/"):
        entry = f"{entry}/"

    existing: List[str] = []
    if gitignore_path.exists():
        try:
            existing = gitignore_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            return False, f"Failed to read .gitignore: {exc}"

    normalized = entry.strip("/")
    candidates = {
        normalized,
        f"{normalized}/",
        f"/{normalized}",
        f"/{normalized}/",
        entry,
    }

    for line in existing:
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if cleaned in candidates:
            return False, None

    try:
        gitignore_path.parent.mkdir(parents=True, exist_ok=True)
        with gitignore_path.open("a", encoding="utf-8") as handle:
            if existing and existing[-1] != "":
                handle.write("\n")
            handle.write(entry)
            handle.write("\n")
    except OSError as exc:
        return False, f"Failed to update .gitignore: {exc}"

    return True, None


def worktree_add(
    branch: str,
    *,
    path: Optional[str] = None,
    base: Optional[str] = None,
    force: bool = False,
    ensure_gitignore: bool = True,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    branch = branch.strip()
    if not branch:
        return 1, "Branch name is required"

    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return 1, error or "No git repository found"

    base_dir: Optional[Path] = None
    created_base = False
    updated_gitignore = False
    gitignore_entry: Optional[str] = None

    if path:
        target = Path(path).expanduser()
        if not target.is_absolute():
            target = repo_root / target
    else:
        base_dir = _select_worktree_base(repo_root)
        if base_dir.exists() and not base_dir.is_dir():
            return 1, f"{base_dir} exists and is not a directory"
        if not base_dir.exists():
            base_dir.mkdir(parents=True, exist_ok=True)
            created_base = True

        try:
            rel_branch = _sanitize_branch_path(branch)
        except ValueError as exc:
            return 1, str(exc)
        target = base_dir / rel_branch

        if ensure_gitignore:
            try:
                gitignore_entry = (
                    base_dir.resolve().relative_to(repo_root.resolve()).as_posix().rstrip("/")
                )
            except Exception:
                gitignore_entry = None
            if gitignore_entry:
                updated_gitignore, err = _ensure_gitignore_entry(
                    repo_root, gitignore_entry
                )
                if err:
                    return 1, err

    if target.exists():
        return 1, f"Target path already exists: {target}"

    branch_exists = _git_branch_exists(repo_root, branch)
    args: List[str] = ["worktree", "add"]
    if force:
        args.append("--force")
    if branch_exists:
        args.extend([str(target), branch])
    else:
        args.extend([str(target), "-b", branch])
        if base:
            args.append(base)

    code, out, err = _run_git(args, repo_root)
    if code != 0:
        message = (err or out or "Failed to add worktree").strip()
        return code, message

    messages: List[str] = [f"Worktree ready at {target}"]
    if branch_exists:
        messages.append(f"Checked out existing branch {branch}")
    else:
        if base:
            messages.append(f"Created branch {branch} from {base}")
        else:
            messages.append(f"Created branch {branch}")
    if created_base and base_dir is not None:
        messages.append(f"Created base directory {base_dir}")
    if updated_gitignore and gitignore_entry:
        messages.append(f"Added {gitignore_entry}/ to .gitignore")

    return 0, " | ".join(messages)


def worktree_remove(
    target: str,
    *,
    force: bool = False,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    target = target.strip()
    if not target:
        return 1, "Worktree path or branch is required"

    repo_root, worktrees, error = worktree_discover(cwd)
    if error or repo_root is None:
        return 1, error or "No git repository found"

    matched: Optional[WorktreeInfo] = None
    normalized = _normalize_branch(target)
    for entry in worktrees:
        if entry.branch and entry.branch == normalized:
            matched = entry
            break

    candidate_path = Path(target).expanduser()
    if matched is None:
        if not candidate_path.is_absolute():
            candidate_path = repo_root / candidate_path
        for entry in worktrees:
            try:
                if entry.path.resolve() == candidate_path.resolve():
                    matched = entry
                    break
            except OSError:
                continue

    if matched is None:
        return 1, f"No worktree found for '{target}'"

    try:
        if matched.path.resolve() == repo_root.resolve():
            return 1, "Refusing to remove the main worktree"
    except OSError:
        pass

    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(matched.path))

    code, out, err = _run_git(args, repo_root)
    if code != 0:
        message = (err or out or "Failed to remove worktree").strip()
        return code, message

    return 0, f"Removed worktree at {matched.path}"


def worktree_prune(
    *,
    dry_run: bool = False,
    verbose: bool = False,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    repo_root, error = _resolve_repo_root(cwd)
    if error or repo_root is None:
        return 1, error or "No git repository found"

    args = ["worktree", "prune"]
    if dry_run:
        args.append("--dry-run")
    if verbose:
        args.append("--verbose")

    code, out, err = _run_git(args, repo_root)
    if code != 0:
        message = (err or out or "Failed to prune worktrees").strip()
        return code, message

    output = (out or "Worktree prune complete").strip()
    return 0, output
