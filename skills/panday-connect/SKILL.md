---
name: panday-connect
description: 'Create an explicit workflow connecting independent skills through defined inputs, outputs, handoffs, validation, and failure handling.'
---

# Panday Connect Skills

Design a repeatable workflow connecting independent skills. Keep each skill's ownership intact and specify what data crosses each handoff. Produce a workflow specification; do not silently modify or install the connected skills.

## Workflow

1. Identify exact skill revisions, owners, user goal, trigger, expected outcome, and any data or authority boundaries.
2. Read each skill contract and relevant resources. Create a capability map showing input, output, side effects, prerequisites, and failure/hold states.
3. Draw the smallest useful sequence or branching graph. For each edge define the artifact, required fields, producer, consumer, validation rule, freshness/fingerprint rule, and behavior when absent or invalid.
4. Define orchestration ownership: who selects the next step, who can ask the user, and which actions require explicit approval. Never infer that one skill's approval authorizes another skill's effects.
5. Specify retries, partial completion, cancellation, duplicate runs, stale results, and recovery. Do not allow a held or failed result to become a success state by omission.
6. Provide one normal example and boundary examples, then validate every handoff against the source contracts. Report if the proposed connection requires changes to a component skill.

## Boundaries

Use Synthesize when the user wants one merged skill. Use Connect when capabilities remain independently useful. Preserve exact revision identity and explicit data flow; do not invent an always-on orchestrator.

## Resources

- [Handoff contract guide](references/handoff-contract.md)
- [Workflow template](assets/workflow.yaml)

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/connect-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
