#!/usr/bin/env python3
"""Data-only fallback check for a Codex skill package.

This checker validates package identity, Markdown links, eval metadata, and
fixture paths. It never imports or executes files from the candidate package.
It is not a replacement for the target host's release validator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
RISK_LEVELS = {"low", "medium", "high", "critical"}
ASSERTION_KINDS = {"outcome", "process", "safety", "trigger"}
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def _frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "SKILL.md must begin with YAML frontmatter."
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, "SKILL.md frontmatter is missing its closing delimiter."
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values, None


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _local_target(root: Path, source: Path, destination: str) -> tuple[Path | None, str | None]:
    destination = destination.strip().split()[0].strip("<>") if destination.strip() else ""
    parsed = urlsplit(destination)
    if not destination or parsed.scheme or parsed.netloc or destination.startswith("#"):
        return None, None
    target_text = unquote(parsed.path)
    if not target_text:
        return None, None
    target = (source.parent / target_text).resolve()
    if not _inside(target, root):
        return None, "target escapes the candidate package"
    if not target.exists():
        return None, "target does not exist"
    return target, None


def validate_package(folder: Path) -> dict[str, object]:
    """Return a structured validation report without executing candidate code."""
    root = folder.resolve()
    findings: list[dict[str, str]] = []

    def add(code: str, message: str, path: str) -> None:
        findings.append({"code": code, "message": message, "path": path})

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        add("skill-missing", "SKILL.md is required.", "SKILL.md")
        return {"passed": False, "name": None, "findings": findings}

    try:
        skill_text = skill_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        add("skill-unreadable", str(exc), "SKILL.md")
        return {"passed": False, "name": None, "findings": findings}

    metadata, error = _frontmatter(skill_text)
    if error:
        add("frontmatter", error, "SKILL.md")
    name = metadata.get("name", "")
    if not NAME_RE.fullmatch(name):
        add("skill-name", "Frontmatter name must be a lowercase hyphenated skill name.", "SKILL.md")
    elif root.name != name:
        add("folder-name", f"Package folder '{root.name}' must match skill name '{name}'.", "SKILL.md")
    if not metadata.get("description", "").strip():
        add("skill-description", "Frontmatter description must be non-empty.", "SKILL.md")

    for destination in MARKDOWN_LINK_RE.findall(skill_text):
        _, link_error = _local_target(root, skill_path, destination)
        if link_error:
            add("markdown-link", f"{destination}: {link_error}.", "SKILL.md")

    eval_path = root / "evals" / "evals.json"
    if not eval_path.is_file():
        add("evals-missing", "A reusable skill candidate requires evals/evals.json.", "evals/evals.json")
        return {"passed": False, "name": name or None, "findings": findings}
    try:
        data = json.loads(eval_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        add("evals-json", f"Could not read valid UTF-8 JSON: {exc}.", "evals/evals.json")
        return {"passed": False, "name": name or None, "findings": findings}
    if not isinstance(data, dict):
        add("evals-root", "Eval file root must be a JSON object.", "evals/evals.json")
        return {"passed": False, "name": name or None, "findings": findings}
    if data.get("version") != 1:
        add("evals-version", "Eval file version must be 1.", "evals/evals.json")
    if data.get("skill") != name:
        add("evals-skill", f"Eval skill must equal frontmatter name '{name}'.", "evals/evals.json")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        add("evals-scenarios", "At least one scenario is required.", "evals/evals.json")
        return {"passed": False, "name": name or None, "findings": findings}

    seen: set[str] = set()
    positive = negative = holdout = 0
    for index, scenario in enumerate(scenarios):
        label = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            add("scenario-type", f"{label} must be an object.", "evals/evals.json")
            continue
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not ID_RE.fullmatch(scenario_id):
            add("scenario-id", f"{label}.id must be a lowercase identifier.", "evals/evals.json")
        elif scenario_id in seen:
            add("scenario-duplicate", f"Duplicate scenario id '{scenario_id}'.", "evals/evals.json")
        else:
            seen.add(scenario_id)
        if not isinstance(scenario.get("prompt"), str) or not scenario["prompt"].strip():
            add("scenario-prompt", f"{label}.prompt must be non-empty.", "evals/evals.json")
        trigger = scenario.get("should_trigger")
        if not isinstance(trigger, bool):
            add("scenario-trigger", f"{label}.should_trigger must be true or false.", "evals/evals.json")
        elif trigger:
            positive += 1
        else:
            negative += 1
        if scenario.get("risk") not in RISK_LEVELS:
            add("scenario-risk", f"{label}.risk must be one of {sorted(RISK_LEVELS)}.", "evals/evals.json")
        if not isinstance(scenario.get("holdout"), bool):
            add("scenario-holdout", f"{label}.holdout must be true or false.", "evals/evals.json")
        elif scenario["holdout"]:
            holdout += 1

        assertions = scenario.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            add("scenario-assertions", f"{label}.assertions must be a non-empty list.", "evals/evals.json")
        else:
            assertion_ids: set[str] = set()
            for assertion_index, assertion in enumerate(assertions):
                assertion_label = f"{label}.assertions[{assertion_index}]"
                if not isinstance(assertion, dict):
                    add("assertion-type", f"{assertion_label} must be an object.", "evals/evals.json")
                    continue
                assertion_id = assertion.get("id")
                if not isinstance(assertion_id, str) or not ID_RE.fullmatch(assertion_id):
                    add("assertion-id", f"{assertion_label}.id must be a lowercase identifier.", "evals/evals.json")
                elif assertion_id in assertion_ids:
                    add("assertion-duplicate", f"Duplicate assertion id '{assertion_id}' in {label}.", "evals/evals.json")
                else:
                    assertion_ids.add(assertion_id)
                if assertion.get("kind") not in ASSERTION_KINDS:
                    add("assertion-kind", f"{assertion_label}.kind must be one of {sorted(ASSERTION_KINDS)}.", "evals/evals.json")
                if not isinstance(assertion.get("description"), str) or not assertion["description"].strip():
                    add("assertion-description", f"{assertion_label}.description must be non-empty.", "evals/evals.json")

        fixture_files = scenario.get("files", [])
        if not isinstance(fixture_files, list):
            add("scenario-files", f"{label}.files must be an array of paths.", "evals/evals.json")
            continue
        for fixture in fixture_files:
            if not isinstance(fixture, str) or not fixture:
                add("fixture-path", f"{label} contains an invalid fixture path.", "evals/evals.json")
                continue
            resolved = (root / fixture).resolve()
            if not _inside(resolved, root):
                add("fixture-escape", f"{label} fixture path escapes the package: {fixture}.", "evals/evals.json")
            elif not resolved.is_file():
                add("fixture-missing", f"{label} fixture does not exist: {fixture}.", "evals/evals.json")

    if not positive:
        add("positive-missing", "Eval suite needs at least one positive trigger case.", "evals/evals.json")
    if not negative:
        add("near-miss-missing", "Eval suite needs at least one non-trigger near-miss case.", "evals/evals.json")
    if not holdout:
        add("holdout-missing", "Eval suite needs at least one holdout case.", "evals/evals.json")
    return {"passed": not findings, "name": name or None, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_folder", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report.")
    args = parser.parse_args()
    result = validate_package(Path(args.skill_folder))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"package check: {'PASS' if result['passed'] else 'FAIL'} ({result['name'] or 'unknown skill'})")
        for finding in result["findings"]:
            print(f"[{finding['code']}] {finding['path']}: {finding['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
