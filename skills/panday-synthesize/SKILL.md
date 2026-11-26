---
name: panday-synthesize
description: 'Merge two or more skills into one coherent skill without losing useful capabilities, safety constraints, lineage, or regression cases.'
---

# Panday Synthesize

Consolidate multiple skill packages into one maintainable skill without flattening distinct behavior into vague prose. Produce a proposed merged candidate and traceability map; do not install it unless separately requested.

## Workflow

1. Identify exact source revisions, intended target host, owner, and requested destination. Preserve read-only copies and fingerprints of every source.
2. Build a capability inventory per source: triggers, procedure, outputs, authority boundaries, safety constraints, dependencies, resources, and proven successful cases. Mark duplicate, complementary, conflicting, and obsolete elements.
3. Resolve conflicts explicitly. Preserve stricter safety and authority rules; do not silently choose between incompatible user-facing promises. Ask only when the unresolved choice changes the result materially.
4. Design one coherent trigger and workflow. Retain distinct methods as named branches or decision points where they serve different inputs. Avoid concatenating source documents or compressing them into generic guidance.
5. Produce the merged package with source-to-destination mapping, retained/changed/omitted rationale, compatibility notes, and regression cases from each parent. Validate links and metadata; do not execute parent scripts.
6. Report fidelity gaps, unresolved decisions, and the exact candidate fingerprint. Request owner review before replacing or publishing source skills.

## Boundaries

Synthesis changes identity and lineage: preserve all parents and their fingerprints. Do not claim full preservation unless every material capability maps to the result and regression cases support it. Use Connect when the skills should remain independent and cooperate in a workflow; use Augment when one skill is the clear base.

## Resources

- [Synthesis mapping rubric](references/synthesis-rubric.md)
- [Parent capability matrix](assets/parent-capability-matrix.csv)

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/synthesize-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
