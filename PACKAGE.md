# Panday Finished Package

This archive contains the completed Panday skill ecosystem:

- `skills/`: the 12 canonical standalone `panday-*` skills
- `cli/`: the standalone Panday CLI source, project metadata, and README
- `lifecycle/`: versioned lifecycle schemas, templates, validators, and tests
- `release/`: strict-validated `.skill` archives and the final validation summary
- `docs/`: the implementation specification and recorded acceptance evidence

Generated Python caches, evaluation workspaces, and temporary run artifacts are
excluded. Install the CLI from `cli/` with `uv tool install --editable .`.
