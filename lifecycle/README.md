# Panday Skill Lifecycle Protocol

This support package defines optional, explicit handoffs for the Panday skill
authoring lifecycle. It is not a callable skill and does not grant approval.
Each skill remains usable without these files or the local validator; in that
case return its ordinary Markdown record and name any evidence needed for a
later handoff. The validator uses only the Python 3.10+ standard library.

## Quick start

```powershell
python -B .agents/panday-lifecycle/lifecycle.py fingerprint .agents/skills/panday-create
python -B .agents/panday-lifecycle/lifecycle.py validate-record path/to/record.json
python -B .agents/panday-lifecycle/lifecycle.py validate-chain records\create.json records\inspect.json
```

The validator reads JSON and hashes files only. It never imports, executes, or
follows commands from a candidate skill. It rejects symbolic links during tree
fingerprinting. Tree identity sorts relative file paths and binds each path,
byte length, and content digest; empty directories and filesystem metadata are
not included. Use `--json` for machine-readable command results.

## Protocol overview

Legacy records use `habi-skill-lifecycle/v1` and remain readable by `lifecycle.py`. New multi-parent records use `panday-skill-lifecycle/v2`; validate them with `validate_v2.py`. V2 binds subject, parents, source snapshot, and input/output fingerprints separately from evidence, review status, and authorization. Validation establishes record consistency only; it does not authorize writes or certify behavior. Changed bytes require fresh evidence and preserve predecessor identities.

Typical optional sequence:

```text
create -> inspect -> evaluate -> fix -> inspect/evaluate -> install -> card
```

This is not a mandatory pipeline. A standalone task can use the relevant skill
and its original Markdown record. Cards summarize supplied evidence and never
promote an earlier status or create an approval.

Read [the protocol contract](references/protocol.md), [record format](schemas/record.schema.json),
and [the comparative study protocol](references/comparative-study.md) for details.
`templates/record.example.json` is illustrative: its all-zero digest is a
placeholder and must be replaced before binding a record to a candidate.
