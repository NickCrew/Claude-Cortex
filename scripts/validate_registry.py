#!/usr/bin/env python3
"""
Validate the skills registry against the JSON schema.

This script validates:
1. registry.yaml structure against registry.schema.json
2. Author references in registry.yaml against authors.yaml
3. Skill path existence
4. Dependency graph for cycles
5. Category consistency

Usage:
    python scripts/validate_registry.py
    python scripts/validate_registry.py --verbose
    python scripts/validate_registry.py --check-paths
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
except ImportError:
    print("Error: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: PyYAML package required. Install with: pip install pyyaml")
    sys.exit(1)


# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
SCHEMA_PATH = SKILLS_DIR / "registry.schema.json"
REGISTRY_PATH = SKILLS_DIR / "registry.yaml"
AUTHORS_PATH = SKILLS_DIR / "authors.yaml"


class RegistryValidator:
    """Validates the skills registry against schema and business rules."""

    def __init__(self, verbose: bool = False, check_paths: bool = False) -> None:
        self.verbose = verbose
        self.check_paths = check_paths
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")

    def error(self, message: str) -> None:
        """Record an error."""
        self.errors.append(message)
        print(f"ERROR: {message}")

    def warn(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)
        if self.verbose:
            print(f"WARNING: {message}")

    def load_yaml(self, path: Path) -> dict[str, Any] | None:
        """Load a YAML file."""
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.error(f"File not found: {path}")
            return None
        except yaml.YAMLError as e:
            self.error(f"YAML parse error in {path}: {e}")
            return None

    def load_json(self, path: Path) -> dict[str, Any] | None:
        """Load a JSON file."""
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            self.error(f"File not found: {path}")
            return None
        except json.JSONDecodeError as e:
            self.error(f"JSON parse error in {path}: {e}")
            return None

    def validate_schema(
        self, registry: dict[str, Any], schema: dict[str, Any]
    ) -> bool:
        """Validate registry against JSON schema."""
        print("\n1. Validating registry against JSON schema...")
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(registry))

        if errors:
            for error in errors:
                path = " -> ".join(str(p) for p in error.path) or "root"
                self.error(f"Schema validation failed at '{path}': {error.message}")
            return False

        self.log("Schema validation passed")
        return True

    def validate_authors(
        self, registry: dict[str, Any], authors: dict[str, Any]
    ) -> bool:
        """Validate that all author references exist in authors.yaml."""
        print("\n2. Validating author references...")
        valid = True
        author_ids = set(authors.get("authors", {}).keys())

        skills = registry.get("skills", {})
        for skill_id, skill in skills.items():
            skill_authors = skill.get("authors", [])
            for author in skill_authors:
                if author not in author_ids:
                    self.error(
                        f"Skill '{skill_id}' references unknown author '{author}'"
                    )
                    valid = False
                else:
                    self.log(f"Skill '{skill_id}' author '{author}' validated")

        if valid:
            self.log("All author references are valid")
        return valid

    def validate_paths(self, registry: dict[str, Any]) -> bool:
        """Validate that skill paths exist."""
        print("\n3. Validating skill file paths...")
        valid = True

        skills = registry.get("skills", {})
        for skill_id, skill in skills.items():
            path = skill.get("path", "")
            full_path = SKILLS_DIR / path

            if not full_path.exists():
                if self.check_paths:
                    self.error(f"Skill '{skill_id}' path does not exist: {full_path}")
                    valid = False
                else:
                    self.warn(f"Skill '{skill_id}' path does not exist: {full_path}")
            else:
                self.log(f"Skill '{skill_id}' path validated: {path}")

        if valid:
            self.log("All skill paths are valid")
        return valid

    def validate_dependencies(self, registry: dict[str, Any]) -> bool:
        """Validate dependency graph for cycles and missing references."""
        print("\n4. Validating dependency graph...")
        valid = True
        skills = registry.get("skills", {})
        skill_ids = set(skills.keys())

        # Check for missing dependencies
        for skill_id, skill in skills.items():
            deps = skill.get("dependencies", [])
            for dep in deps:
                if dep not in skill_ids:
                    self.error(
                        f"Skill '{skill_id}' has unknown dependency '{dep}'"
                    )
                    valid = False
                else:
                    self.log(f"Skill '{skill_id}' dependency '{dep}' validated")

        # Check for cycles using DFS
        def has_cycle(node: str, visited: set, rec_stack: set) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for dep in skills.get(node, {}).get("dependencies", []):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    self.error(f"Circular dependency detected: {node} -> {dep}")
                    return True

            rec_stack.remove(node)
            return False

        visited: set[str] = set()
        for skill_id in skills:
            if skill_id not in visited:
                if has_cycle(skill_id, visited, set()):
                    valid = False

        if valid:
            self.log("No circular dependencies found")
        return valid

    def validate_categories(self, registry: dict[str, Any]) -> bool:
        """Validate that skill categories match defined categories."""
        print("\n5. Validating category consistency...")
        valid = True

        defined_categories = set(registry.get("categories", {}).keys())
        skills = registry.get("skills", {})

        for skill_id, skill in skills.items():
            categories = skill.get("categories", [])
            for cat in categories:
                if cat not in defined_categories:
                    self.error(
                        f"Skill '{skill_id}' uses undefined category '{cat}'"
                    )
                    valid = False
                else:
                    self.log(f"Skill '{skill_id}' category '{cat}' validated")

        if valid:
            self.log("All categories are valid")
        return valid

    def validate_statistics(self, registry: dict[str, Any]) -> bool:
        """Validate that statistics match actual counts."""
        print("\n6. Validating statistics...")
        valid = True

        skills = registry.get("skills", {})
        stats = registry.get("statistics", {})

        # Count skills by status
        status_counts = {"active": 0, "maintenance": 0, "deprecated": 0, "archived": 0}
        for skill in skills.values():
            status = skill.get("status", "active")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Validate counts
        if stats.get("total_skills", 0) != len(skills):
            self.warn(
                f"Statistics total_skills ({stats.get('total_skills', 0)}) "
                f"doesn't match actual count ({len(skills)})"
            )

        if stats.get("active_skills", 0) != status_counts["active"]:
            self.warn(
                f"Statistics active_skills ({stats.get('active_skills', 0)}) "
                f"doesn't match actual count ({status_counts['active']})"
            )

        self.log("Statistics validation complete")
        return valid

    def run(self) -> bool:
        """Run all validations."""
        print("=" * 60)
        print("Skills Registry Validation")
        print("=" * 60)

        # Load files
        schema = self.load_json(SCHEMA_PATH)
        registry = self.load_yaml(REGISTRY_PATH)
        authors = self.load_yaml(AUTHORS_PATH)

        if not all([schema, registry, authors]):
            return False

        # Run validations
        results = [
            self.validate_schema(registry, schema),
            self.validate_authors(registry, authors),
            self.validate_paths(registry),
            self.validate_dependencies(registry),
            self.validate_categories(registry),
            self.validate_statistics(registry),
        ]

        # Summary
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\nErrors found:")
            for error in self.errors:
                print(f"  - {error}")

        if all(results):
            print("\nRegistry validation PASSED")
            return True
        else:
            print("\nRegistry validation FAILED")
            return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate skills registry against schema"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--check-paths",
        action="store_true",
        help="Treat missing skill paths as errors (default: warnings)",
    )
    args = parser.parse_args()

    validator = RegistryValidator(verbose=args.verbose, check_paths=args.check_paths)
    success = validator.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
