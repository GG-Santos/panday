---
name: panday-fix
description: 'Repair an existing skill when it misses its intended purpose or exhibits a supported high frequency failure; preserve successful behavior and regressions.'
---

# Panday Fix

Repair one supported failure of an existing skill's promise. Preserve the
original evidence and successful behavior, identify the cause before changing
instructions, and verify the repair against the same failure and relevant
regressions. Do not treat every poor outcome as a skill defect.

## Route the failure first

- Wrong skill selected, wrong copy loaded, runtime setup or missing trace:
  diagnose the host routing/setup first with its available diagnostic capability; if unavailable, state the uncertainty before editing source.
- Candidate contract, packaging, or unsafe-resource defect: inspect with Panday Inspect.
- Unclear comparative effect, rubric, or output quality: use Panday Evaluate.
- A working skill needs a new capability: Panday Augment.
- No skill covers the demonstrated need: Panday Create.

Fix only when evidence supports a defect in the current promise or behavior.

## Repair procedure

1. **State the mismatch.** Record expected behavior, observed result, task and
   inputs, exact selected/loaded revision where known, project rules, tools,
   permissions, and the evidence source. Keep secrets out. If identity or
   context is missing, make the diagnosis provisional and name the evidence
   needed to resolve it.
2. **Protect the baseline.** Preserve the original candidate, reported output,
   and evaluation rubric. Capture the failure before editing. Build a minimal
   reproducer and a nearby successful case. If reproduction could cause an
   unauthorized write, network action, cost, or other harm, use retained traces
   or an inert fixture instead; never repeat the unsafe effect.
3. **Test the cause.** Distinguish among wrong routing/loading, missing or
   conflicting context, unavailable capability, ambiguous request, flawed
   evaluation, and faulty instructions. State a falsifiable cause linking the
   evidence to the failure. If two causes remain plausible, run the narrowest
   safe check that discriminates between them before editing.
4. **Make a scoped correction.** Change only what the supported cause requires:
   trigger boundary, ordering, decision condition, default, output contract,
   resource, or deterministic helper. Preserve the original name and invocation
   unless the user authorized a migration. Do not broaden scope, edit evidence
   or rubrics to improve the score, or discard successful behavior.
5. **Retest comparably.** Re-run the original failure, a successful path, a
   boundary/near-miss case, and relevant safety constraints with the same
   inputs and conditions. Run structural validation and refresh evidence
   affected by changed bytes. Retain prior results and label conditions that
   changed; do not pool unlike runs. If the failure is not resolved, preserve
   the new result and continue diagnosis rather than claiming success.
6. **Return the repair.** Use the [repair record](templates/skill-repair-record.md)
   to state baseline, cause, exact change, retest evidence, regressions, and
   open checks. Route any remaining issue to the appropriate skill above.

## Optional lifecycle handoff

Repair works standalone. For composition, link the predecessor record and bind
the revised candidate to its new fingerprint in the optional
`.agents/panday-lifecycle` protocol. Byte-bound findings from the old
revision are not current for changed bytes; refresh the affected inspection or
evaluation claims.

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
- [Work record](assets/fix-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
