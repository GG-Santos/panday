# Panday CLI

Install the local command with `uv tool install --editable .agents/panday-cli`, then run `panday --help`. Runtime operations use Python standard library. Smoke checks should work from outside the repository: `panday --help` and `panday --json doctor`.

## Command reference

Global options such as `--json` go before the command. Human-readable output is the default; JSON mode writes the result to stdout.

- `panday --version`: print the installed CLI version.
- `panday doctor` / `panday --json doctor`: inspect local setup; authentication values are never printed.
- `panday init`: create the local `~/.panday/config.toml` if absent.
- `panday skills show <skill-name-or-local-path>`: show a configured local skill's path and tree fingerprint.
- `panday skills inspect <source> [--ref REF] [--subpath PATH] [--skill NAME] [--report-dir DIR]`: inspect exact candidate bytes without executing candidate code.
- `panday eval validate <skill-folder-or-evals.json>`: validate a suite.
- `panday eval init <skill-folder-or-evals.json> [--output PATH]`: create a starter suite; refuses to overwrite an existing file.
- `panday eval workspace <evals.json> [--output PATH]`: create a run-results skeleton; this does not execute model tasks.
- `panday eval report <report.json-or-results.jsonl> [--evals PATH]`: display a JSON report or summarize JSONL run records.
- `panday eval benchmark <results.jsonl> [--evals PATH] [--policy PATH] [--output PATH]`: calculate paired summaries and optionally apply a gate policy.
- `panday eval gate <report.json> --policy <policy.json>`: apply explicit evidence and quality thresholds.
- `panday lifecycle fingerprint <skill-folder...>`, `validate-record <record.json>`, and `validate-chain <record.json...>`: report fingerprints or structurally validate records; these commands do not grant approval.

## Discovery and source operations

- `panday skills search <query> [--owner <github-owner>]` queries skills.sh and merges configured local registry matches. The skills.sh endpoint mirrors the current Vercel Skills CLI but is undocumented, so results are experimental, cached for up to 24 hours on network failure, and may omit valid skills. Popularity is not quality or safety evidence.
- `panday skills list` lists skills found in configured local registry paths (`~/.panday/config.toml`, `registries.paths`). `panday skills list <query> --source skills.sh` performs a remote query; there is no stable public catalog-wide list API.
- `panday skills inspect <source> [--ref REF] [--subpath PATH] [--skill NAME]` inventories local or GitHub candidate bytes without executing scripts.
- `panday skills install <source> --project DIR [--ref REF] [--subpath PATH] [--skill NAME]` previews a local or GitHub skill. Apply requires the current `--fingerprint`; destination collisions are rejected. GitHub public/private archives use existing `GH_TOKEN` or `GITHUB_TOKEN` environment credentials, never command-line tokens. Archives are bounded and reject unsafe paths/symlinks.

To configure local curated folders, add paths to `~/.panday/config.toml` after running `panday init`:

```toml
version = 1

[registries]
paths = ["C:/Users/me/curated-skills", "H:/team/approved-skills"]
```

## Migration

`panday skills migrate <source> --to codex|claude --target DIR [--from-provider codex|claude]` previews and fingerprints the target package. Claude-to-Codex creates missing Codex interface metadata; Codex-to-Claude validates Claude manifest constraints and preserves Codex metadata as inert files with a warning. Apply requires the matching preview fingerprint and an absent target. This is packaging and metadata migration: host activation and behavioral equivalence are not certified. Provider-specific tools and integrations remain manual review items.

## Evaluation and lifecycle

`panday eval validate` checks scenario contracts; `workspace` creates a result skeleton; `benchmark` computes paired quality/score/time/token summaries, optional `cost_usd` summaries, variability, unmatched runs, and incomplete scenarios. Monetary cost is never estimated when absent. `gate` returns HOLD when required evidence is missing and applies explicit policy thresholds when evidence is present. `benchmark --policy` applies the same decision rule, includes its gate result in the report, and returns the corresponding gate exit code. With `--evals`, `kind: process` assertions are reported separately from quality pass rates and scores, with counts by arm. A missing process assertion, or one explicitly recorded with `status: unassessed`, is counted as unassessed rather than as a task failure; top-level `process_assertions` and process gate policies describe the `with_skill` arm, while `by_variant` retains baseline and assisted counts. `process_assessment_complete` describes trace coverage for the `with_skill` arm. Assessed assertions require a boolean `passed` and non-empty `evidence`. `complete` describes scenario/pair coverage, not process-assessment coverage. For eval definitions containing process assertions, the benchmark derives `score` from non-process assertions unless a run supplies an explicit `quality_score`; it does not reuse the legacy `score` field, which could contain process checks. Gate policies can set `required_complete_pairs` and `minimum_repetitions`; the report must include those counts or the gate holds. They can also opt into `minimum_process_assessment_rate` (HOLD when trace coverage is too low) and `maximum_process_failures` (HOLD when process evidence is absent or unassessed; BLOCK when failures exceed the limit). The CLI does not run model evaluations. Use the included skill-creator runner for paired model runs and keep its raw outputs. Lifecycle commands structurally validate v1/v2 records and do not authorize operations.

For development: `uv run --project .agents/panday-cli panday --help`. Tests: `python -B -m unittest discover -s .agents/panday-cli/tests`. Candidate code is never executed by the CLI.

## Exit codes

- `0`: command succeeded, including a gate `ALLOW`.
- `2`: invalid arguments or an operation error. `argparse` usage errors also use `2`.
- `3`: an evaluation policy returned `BLOCK`.
- `4`: an evaluation returned `HOLD`, or a valid remote search returned no results.
