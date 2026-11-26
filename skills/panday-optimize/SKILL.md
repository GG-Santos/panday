---
name: panday-optimize
description: 'Improve an existing skill on a specific task by comparing alternate routes against a baseline while protecting broader quality and safety.'
---

# Panday Optimize Skill

Find and validate a better path for one target task while preserving the skill's broader promise. Optimization is a comparative improvement claim, so retain a baseline and compare equivalent cases.

## Resource scope

Classify the request before loading linked resources:

- For an ordinary optimization task, read this `SKILL.md`, the supplied target skill and task evidence, and the matched-experiment protocol. Read the experiment-record schema only when producing that record; read the decision rubric when selecting a disposition. Load the task-specialist agent only when delegating a bounded analysis.
- Do not read this package's own `evals/`, `tests/`, `scripts/`, or `assets/optimize-work-record.md` for an ordinary target-skill optimization. Those files describe testing or maintaining Panday Optimize itself, not the target skill's workflow.
- Read this package's evals, tests, scripts, and package-maintenance assets only when the user asks to create, edit, inspect, or validate the Panday Optimize package. A generated target skill's own checker or tests may be used when they directly validate an authorized target edit.
- If the task is only to interpret supplied results and does not authorize new trials or edits, analyze the supplied evidence and report a bounded decision; do not load package-maintenance resources or invent additional runs.

## Workflow

1. Define the target task, success criteria, constraints, current skill revision, and baseline outcomes. Separate user-perceived friction from measured failure.
2. Diagnose the bottleneck using run traces, representative cases, and resource loading. Do not rewrite before identifying what costs or degrades the result.
3. Generate a small set of materially different approaches. Prefer focused changes: trigger precision, decision order, a reference, a reusable asset, or a bounded script. State expected benefits and possible regressions for each.
4. Compare candidate and baseline on matched representative tasks with the same tools and conditions. Match by case and repetition; report missing pairs. A paper walkthrough or designed handoff count is not an observed run or measured result. Include routing, quality, safety, time/cost where available, and cases outside the optimization target.
5. Keep the change only when the target improves and the agreed safety and regression floors hold. If evidence is incomplete, report an experiment rather than an optimization verdict.
6. Return the candidate, baseline/candidate identities, run evidence, tradeoffs, regressions, and rollback path. Do not install or promote without separate authority.

In the report, show the target metric beside quality and safety for each route.
List each safety and out-of-target case with its observed result. If no such
case was run, mark it `not assessed`; do not treat a proposed safeguard as a
passing check. Reject any candidate with a critical safety failure even when
its target metric improves. Keep duration and token changes visible when the
candidate trades them for the target gain.

## Routing

Use Fix when the skill repeatedly fails its existing promise. Use Augment when adding a new capability. Use Evaluate to design broader adoption evidence. Optimization changes the route to an existing outcome, not the outcome contract.

## Resources

- [Optimization experiment protocol](references/experiment-protocol.md)
- [Experiment record](assets/experiment-record.json)

The links above are task-scoped: use the record schema when you create a record, and do not load this package's test or maintenance files unless the task is about this package.

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/optimize-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
