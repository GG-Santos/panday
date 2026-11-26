# Frozen discovery task context

The request is to review Python dependency updates in a repository. The user has not supplied a repository, package manager, operating-system target, or lockfile, so do not assume the target uses `uv`.

The frozen search response contains 13 catalog results. `uv-deps` is a direct Python update/audit candidate, but its documented workflow requires `uv`, a Python project using `pyproject.toml`, Git worktrees, and network access. The exact `SKILL.md` is snapshotted, but package retrieval was held because the full GitHub archive contains a symbolic link; do not infer a candidate-specific malicious behavior from that repository-level failure.

`dependency-updates` is a broader repository-automation workflow that configures Dependabot and optional runtime version checks. It may fit a request to establish ongoing automated updates, but it does not promise an interactive audit or update of a specific dependency. A read-only package inspection succeeded at the fingerprint in `source-review-dependency-updates/inspection.json`.

Catalog install counts are time-bound discovery signals only. The source snapshots and inspection records are the stronger evidence. Do not install or execute any candidate.
