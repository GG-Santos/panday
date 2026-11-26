---
name: panday-migrate
description: 'Migrate a skill package to a named host such as Codex or Claude while preserving behavior, resources, and unsupported-feature reporting.'
---

# Panday Migrate Skill

Convert a selected skill package for a named target host while preserving its intended behavior, safety rules, and resource relationships. Migration changes packaging and host-specific metadata; it must not silently redesign or install the source.

## Workflow

1. Resolve the exact source folder/revision, target provider, and destination. If source or destination is ambiguous, stop before writes. Supported initial targets: Codex and Claude.
2. Inventory source files, metadata, host-specific features, invocation syntax, tools, references, scripts, assets, evals, and links. Never execute source scripts. Preserve the original unchanged.
3. Produce a read-only migration plan mapping each source construct to the target construct. Classify each as preserved, transformed, unsupported, or requiring owner choice. Keep behavior and authority limits; do not invent target capabilities.
4. Validate target conventions against the installed target documentation or the bundled provider reference. If unavailable, mark conformance unverified and use a conservative conversion.
5. Preview all output paths and bytes. Applying requires explicit user authorization for this source and destination and a still-matching preview fingerprint. Do not overwrite unrelated files; preserve user-owned target files.
6. Validate the converted package structurally, check local links and metadata, and report source/target fingerprints, changed files, unsupported features, warnings, and rollback steps.

## Modes

Support scan-only inventory, plan-only mapping, doctor (host readiness), preview/dry-run, authorized apply, target validation, and a migration report. The Panday CLI exposes corresponding `panday skills migrate` modes. If the CLI or provider docs are unavailable, complete a manual plan and state that host validation was not performed.

## Security

Do not transmit private source content without authorization, print or persist credentials, invoke candidate code, or mutate the source. Use existing authenticated provider connections only. A successful conversion does not establish security, quality, or install eligibility.

## Resources

- [Provider mapping rubric](references/provider-mapping.md)
- [Migration report](assets/migration-report.md)

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/migrate-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
