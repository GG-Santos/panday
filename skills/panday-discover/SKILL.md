---
name: panday-discover
description: 'Find existing agent skills for a task, compare source and host fit, and report evidence-backed candidates before creation or installation.'
---

# Panday Discover

Find existing skill candidates that could help with the user's stated task. Return useful candidates and evidence so the user can choose; discovery is not a security approval or an install.

## Workflow

1. Restate the task as a short capability query. Preserve platform, language, tools, and constraints that affect fit. If the request is broad, split it into a few search concepts.
2. Search the sources the user named first. Otherwise inspect configured Panday registries (`panday skills search`) and the public skills.sh catalog where network access is available. Do not imply the catalog is exhaustive. If search is unavailable, search supplied local paths and state the limitation.
3. For each candidate capture exact name, source URL/path, publisher/repository, supported host/platform, stated purpose, last observed revision when available, and the evidence used to judge fit. Open the candidate's SKILL.md and relevant metadata when possible; a search snippet alone is weak evidence.
4. Rank by task fit, scope match, compatibility, maintenance evidence, and provenance. Popularity/download counts are discovery signals only; they do not establish quality, safety, or suitability. Mark unknowns instead of inferring them.
5. Present a concise shortlist with why each fits, mismatches, provenance, confidence, and next action. Recommend Inspect before installing an unfamiliar candidate; route explicit install requests to Install. If no viable candidate exists, explain the search boundary and offer Create only when the capability is genuinely missing.

## Boundaries

Do not run candidate code, install implicitly, treat ranking as endorsement, or send private source content to a remote search. For private repositories, use only an existing authorized connection and do not expose credentials. Distinguish source discovery from source review and host compatibility.

## Resources

- [Source and ranking rubric](references/discovery-rubric.md)
- [Shortlist template](assets/shortlist.md)
- CLI: `panday skills search <query> [--owner <owner>]` queries skills.sh experimentally and merges configured local results; `panday skills list` lists configured local registry entries. The search endpoint is undocumented, cached briefly, and may omit valid skills.

## Package resources
Package evals, tests, and the checker script define and validate this Panday package; do not load them for ordinary user tasks. Run the checker against a target package only when the workflow requires structural validation. Load the task-specialist file only when delegating; load the work-record template only when producing a work record.


- [Task specialist role](agents/task-specialist.md)
- [Decision rubric](references/decision-rubric.md)
- [Work record](assets/discover-work-record.md)
- Run `python scripts/check_package.py <skill-folder>` for a data-only structural check.
- Task cases: [evals/evals.json](evals/evals.json); structural test: [tests/test_package.py](tests/test_package.py).
