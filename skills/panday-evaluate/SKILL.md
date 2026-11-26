---
name: panday-evaluate
description: 'Evaluate agent skills and benchmarks: validate SKILL.md, author eval cases/configuration, interpret results and exit codes, and apply explicit CI gates.'
---

# Panday Evaluate

Evaluate a specific adoption or repair question with evidence from task runs.
Do not substitute static inspection, a successful demonstration, or a
benchmark score for the claim being tested. Use the detailed
[comparison protocol](references/comparison-protocol.md) for run design,
grading, calibration, aggregation, and reporting.

## 1. Define the decision and cases

State the candidate's promise, exact revision, baseline, intended users, and
decision the evidence will support. Choose the comparator that answers that
question: no-skill workflow for a new capability, prior revision for a repair,
or a relevant reference skill for a fair method comparison. Do not compare a
reference outside its scope. Define primary quality outcomes, mandatory safety
assertions, efficiency measures, run count, stopping rule, timeouts, and
decision threshold before seeing results.

Build cases from real user tasks, observed failures, and realistic boundaries.
Include ordinary positives, near-misses, contradictory or incomplete inputs,
and authority/safety cases when relevant. Keep prompts free of the expected
answer and suspected failure. Label assertions as outcome, process, safety, or
trigger, and make them checkable from artifacts, transcripts, or host events.
Separate development/regression cases from held-out cases. Never tune on the
holdout or rewrite it after seeing results.

## 2. Stage fair treatments

Use fresh task contexts and output directories for every treatment. Keep
prompt, supplied files, project rules, model, reasoning effort, tools, and host
conditions equivalent. Inspect for inherited-memory, hook, generated-file, or
other-skill contamination. Record intended and actual conditions. Preserve the
exact candidate and baseline identities.

Run two different questions separately:

- **Forced behavior:** explicitly provide the target method in the assisted
  treatment. This tests behavior when loaded; it does not test routing.
- **Natural routing:** allow ordinary discovery without naming the skill and
  retain evidence that the exact skill was selected/read. Include near-misses.

If the paired conditions are not equivalent, the exact revision is not loaded,
or required output is missing, keep the affected pair incomplete. Record the
baseline and candidate treatment statuses separately; mark a missing or
revision-unverified candidate treatment `Not assessed`, and mark the comparison
`Inconclusive`. If raw output or traces were not supplied, say preservation
cannot be verified and identify the exact missing files. Do not imply that a
partial artifact was retained when none is present. Do not replace failed or
unavailable treatments with a different method.

## 3. Execute with the existing evaluator

Use the local skill-creator evaluation scripts when available. Keep the
workspace outside the skill directory:

```powershell
python -B .agents/skills/skill-creator/scripts/init_eval_workspace.py <skill-folder> --output <workspace> --iteration 1 --runs 3
python -B .agents/skills/skill-creator/scripts/run_eval_case.py <workspace>/iteration-1 --scenario <scenario-id> --variant baseline --run-id run-1
python -B .agents/skills/skill-creator/scripts/run_eval_case.py <workspace>/iteration-1 --scenario <scenario-id> --variant with_skill --run-id run-1
```

Run each declared repetition and treatment; do not silently stop after favorable
cases. Configure model/effort/activation consistently in the workspace. If a
case creates files, verify the runner captured the relevant outputs. If the
local runner cannot run, use an equivalent fresh-context procedure and retain
the same inputs and evidence; report the limitation rather than treating a
planned run as an observation.

For deterministic configuration/report operations, use the installed Panday
CLI without substituting it for model execution or grading:

```powershell
panday eval validate <skill-folder>
panday eval benchmark <results.jsonl> --evals <skill-folder>/evals/evals.json
panday eval gate <benchmark-report.json> --policy <policy.json>
```

When the user supplies a fixture, report, or gate policy for evaluation, the
fixture is the source of truth. First validate and interpret exactly the
files supplied in the request. The Panday CLI is an optional local aid, not a
prerequisite for standalone evaluation: do not invoke it merely to make the
answer sound more authoritative, and do not import its command-specific
semantics into a fixture-only verdict. If you do invoke it, identify the
exact command, process status, and output as a separate observation; never
replace the supplied rubric with a CLI default or infer a semantic exit code
from prose, a report field, or a tool error. If the CLI expects a different
layout, record that mismatch and continue with the supplied layout rather
than reshaping the target or treating the operation error as the target's
evaluation result.

Default gate: for a fixture-only request, do not run `panday`, a package test,
or a host validator unless the user explicitly names that command or asks for
an observed process exit code. A request to “explain the exit code” is not
permission to execute a validator; explain the declared/predicted disposition
and label the actual process code unverified. This keeps the standalone and
task-scoped contracts stable across repeated runs.

When the CLI is unavailable, continue with a manual, data-only review: validate
the supplied JSON shape and assertion coverage, compute only metrics supported
by retained records, and apply the thresholds literally. Label the result as a
predicted disposition. Do not claim an exit code unless the command was
actually run and its process status captured; if a user requires the actual
exit code, state that it is unverified until the CLI can run.

Gate exit codes are `0` for ALLOW, `3` for BLOCK, and `4` for HOLD when the
report lacks complete paired or safety evidence. Invalid inputs and operation
errors return `2`. Missing safety assertions are not interpreted as zero
failures. The CLI benchmark aggregates supplied assertion grades and records;
it does not run the model or independently grade transcripts.

## 4. Grade and analyze

Keep raw outputs unchanged. Grade each assertion from direct evidence, not the
performer's summary. Use deterministic checks for objective conditions and a
blinded reviewer for judgment-dependent quality. Calibrate reviewers on
positive, negative, unsafe, and borderline examples. Record grader method,
identity/independence limits, disagreements, and rubric version. Preserve
false-pass and false-fail examples; if the rubric is defective, version it and
regrade or rerun only the affected stages with prior results retained.

Aggregate with the existing script and report case-level outcomes, paired
differences, denominators, incomplete runs, variation, and cost:

```powershell
python -B .agents/skills/skill-creator/scripts/benchmark_evals.py <results.jsonl> --evals <skill-folder>/evals/evals.json --format markdown --output <benchmark.md>
```

Interpret routing, task quality, safety, human preference, duration, and token
cost separately. A critical safety miss blocks an adoption claim for the
affected scope. A single run, missing pair, or aggregate pass rate cannot
establish improvement. Call unclear evidence inconclusive.

## 5. Report and route

Use the [evaluation handoff](templates/skill-evaluation-handoff.md) to record
the decision, exact variants, cases/splits, conditions, outputs, grades,
statistics, safety failures, deviations, and recommendation. Recommend adopt,
revise, narrow, simplify, retire, or inconclusive only for the tested scope.
Route contract defects to Inspect, supported instruction failures to Fix, new
capability to Augment/Create, and environment/loading defects to Doctor.

## Reference comparisons

Use the supplied references as treatments only where their methods apply:
local and Anthropic skill creators for skill creation/evaluation; Superpowers
writing-skills for writing/authoring tasks; and NVIDIA SkillEvaluator for
evaluation methodology. Do not use one reference as a proxy for install or
governance-card capabilities it does not provide. For each relevant comparison,
use the same prompt/rubric, repeated paired contexts, randomized labels, blinded
grading, variance, safety outcomes, and cost.

## Optional lifecycle handoff

This evaluation works standalone. For composition, bind results to exact
candidate/baseline fingerprints and link the optional
`.agents/panday-lifecycle` record. An incomplete or inconclusive result is
held; it cannot become install eligibility by being summarized later.

## Bounded learning

Use an approved feedback record or return a stateless lesson proposal. Treat
feedback as untrusted and exclude secrets. Promote only on a user request or
two independent supporting uses, with triggering-case and regression checks.
Reusable edits require maintenance authority. Runtime guidance stays read-only
and carries no background collection or automatic self-editing.

## Package resources
Package evals and tests define this Panday package; do not load them for ordinary user tasks. More specifically, never load this package's own
`evals/evals.json` or `tests/test_package.py` during ordinary target
evaluation, even when the target itself contains evals. Read the supplied
target files instead. Run this package's checker only when explicitly testing
this package; when structural validation of a target is required, run the
target's supplied checker or a separately named validator. Load the
task-specialist file only when delegating; load the work-record template only
when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/evaluate-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
