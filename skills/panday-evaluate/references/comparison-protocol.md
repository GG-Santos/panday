# Comparison protocol

Use this protocol for paired skill evaluations and relevant reference
comparisons. Its procedures apply across candidate creation, repair, and
adoption; Panday Evaluate owns the decision and report.

## Before dispatch

- Bind treatment revisions, fixture and rubric bytes, allowed inputs, expected activation, configuration and outcome captures. Separate author-visible cases from the independent holdout and prevent grader answer keys from reaching performers or graders.
- Keep normal host policies, requested project rules, tools, starting files and task inputs equivalent. Freeze previous versions. Record intended and actual conditions separately. A baseline with candidate-derived guidance or unknown isolation stays unassessed. Forced loading checks behavior under the imposed conditions. Use natural host routing evidence for triggering and near-misses.
- Declare the sample size, repeat conditions, stop conditions and timeout handling. Retain partial outputs and reconcile possible external effects before retrying. If no safe or authorized runner is available, return the frozen plan and explicitly missing observations.

## Grading and instrument repair

- Retain outputs unchanged. Provide the evaluator the necessary task context and observed artifacts. When blinded, keep treatment mapping outside grader inputs. Record assessor method, actual configuration, independence limits and assertion-level evidence.
- Check the current evaluator against known positive, negative, unsafe and borderline examples. Classify false passes and false failures. A calibration change or material configuration change requires renewed reliability evidence for the affected claims.
- A task and rubric mismatch may invalidate a criterion even when the grader followed it. Separate task defect, capture defect and grading defect. Version the affected instrument, retain original outputs and grades, document which conditions changed, and rerun the affected stage. Re-execute treatments when inputs, controls or capture were invalid. Keep original and revised judgments attributable to their own instruments.

## Reporting

- Report per-case outcomes, including selected and actually observed loaded guidance, severe failures, incomplete treatments, evidence limits, repeated-run variability and any measured cost. State when there was only one sample. A trace supports the observed event. An aggregate cannot erase failed requirements or missing cases.
- Link the adoption recommendation to the demonstrated scope and comparison. Record inconclusive and worse-than-baseline findings where supported. Keep a material harm hold scoped to the affected context and leave consequential decisions with the existing owner.

## Reference treatments and repeated comparison

Select a reference only for a capability it actually covers. The local and
Anthropic skill creators are relevant comparators for skill creation and
evaluation; Superpowers writing-skills is relevant to skill-writing method;
NVIDIA SkillEvaluator informs evaluation design and grading. It is not a
competing skill whose scores can be compared on unrelated tasks. Install and
Card tasks with no comparable reference should use a no-skill/project baseline
and be reported as Panday-only evidence.

For a material architecture or adoption claim, use at least five fresh runs
per scenario and condition, with treatment order randomized within each pair.
Increase repetitions when observed variance prevents the predeclared comparison
from being resolved; otherwise report the result as inconclusive. Keep
conditions paired, preserve time/token cost and severe failures, and blind the
grader to treatment identity until assertion grades are locked. A static
reference review is not a paired behavior result.

Use the existing skill-creator workspace and evaluation tools rather than
creating a parallel runner:

```powershell
python -B .agents/skills/skill-creator/scripts/init_eval_workspace.py <skill-folder> --output <workspace> --iteration 1 --runs 5
python -B .agents/skills/skill-creator/scripts/run_eval_case.py <workspace>/iteration-1 --scenario <scenario-id> --variant baseline --run-id run-1
python -B .agents/skills/skill-creator/scripts/run_eval_case.py <workspace>/iteration-1 --scenario <scenario-id> --variant with_skill --run-id run-1
python -B .agents/skills/skill-creator/scripts/benchmark_evals.py <results.jsonl> --evals <skill-folder>/evals/evals.json --format markdown --output <benchmark.md>
```

Use the stored `execution_order` in `run-plan.json` to dispatch baseline and
assisted arms in the randomized order; preserve actual start times in run
records. If a reference's intended scope covers only a subset, use repeated
`--scenario <id>` options to create the same narrow task suite for its baseline,
Panday, and reference arms. Do not include unrelated routing or capability
assertions in a reference score. For reference runs, initialize against the Panday eval suite while
supplying `--treatment-skill <frozen-reference-skill-dir>`. This keeps the
prompt, fixtures, and assertions identical while loading the exact reference
package as the treatment. The executor verifies the reference tree fingerprint
before each run. Retain its original source identity and report any
host-specific adaptation. Never rename or silently rewrite the reference to
make it appear native to the host. Keep raw outputs and label mapping separate
until grading is locked.
