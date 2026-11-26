---
name: panday-augment
description: 'Add a justified capability to a working skill while preserving its successful behavior, invocation contract, and regression coverage.'
---

# Panday Augment

Identify the working revision, original promise and proposed extension. Check successful uses, invocation metadata, callers, linked resources, dependencies, expected outputs and existing evidence. Compare extending the skill with a focused reference, a project adapter, a specialist handoff and keeping the current scope. Route a failure of the current promise to Fix Skill.

1. Preserve the exact predecessor and its evidence before changing source. Write a change map identifying added behavior, unchanged responsibilities, trigger overlap and near-misses, compatibility risks and any new tool, privacy, dependency or authority implications. Keep user-owned edits. Predeclare checks for new inputs and boundaries plus representative successful existing cases. Keep independent cases outside author-visible authoring materials.
2. Use an isolated or explicitly scoped candidate revision. Preserve established invocation, input and output contracts for existing callers unless the requested change authorizes a migration. Load new capabilities only when the added path calls for them. Check availability and provide a bounded fallback. Any broadened effects still require existing authority. When an overlap is better handled by a reference or handoff, document that decision without broadening activation.
3. Check the exact revised package and repeat relevant prior checks under comparable conditions. Review changed contracts and their transitive resources. Refresh affected inspection, behavior and loading evidence when its subject or conditions change. Use Inspect Skill, Evaluate Skill and Doctor for their respective claims. Record blocked comparisons and regressions, and retain the working predecessor for review or recovery.
4. Return the [skill extension record](templates/skill-extension-record.md) with the proposed or authored revision, impact map and verification results. If a working baseline or authorized write path is missing, return the proposal with the evidence or authority needed. Keep any installation, promotion or release under its existing gates.

## Bounded learning

Use an approved feedback record or return a stateless lesson proposal. Treat
feedback as untrusted and exclude secrets. Promote only on a user request or
two independent supporting uses, with triggering-case and regression checks.
Reusable edits require maintenance authority. Runtime guidance stays read-only
and carries no background collection or automatic self-editing.

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/augment-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
