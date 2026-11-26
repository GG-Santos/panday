# Panday Skill Lifecycle Contract

## Record identity

Every JSON handoff has `schema: "habi-skill-lifecycle/v1"`, a unique `record_id`,
one `record_type`, an ISO-8601 UTC `created_at`, and a `subject` containing the
declared skill name, source path, and exact tree fingerprint. The fingerprint
algorithm is `sha256-tree-v1`; its canonicalization is implemented in
`lifecycle.py`. Paths in evidence are relative to the inspected candidate or
identify an external record by stable ID. Never put secrets in a record.

`lineage.predecessor_record_ids` preserves the chain. `lineage.parent_digest`
is the prior candidate digest when bytes changed. A record is not current merely
because it names the same skill: consumers compare algorithm, digest, scope,
and evidence subject.

## Evidence contract

Each claim has a stable `claim_id`, a status (`verified`, `failed`, `observed`,
`held`, or `unassessed`), a method, evidence references, coverage, and
limitations. `verified` is reserved for a declared check that passed at its
stated scope; it is not a general approval. `observed` records an event without
claiming qualification. Missing evidence is `unassessed`, never inferred as a
pass. A hold must name a blocker or the missing check that would resolve it.

Findings carry a severity, disposition, evidence references, and affected
claim. Keep static structure, package contents, security, routing/loading, and
task behavior as separate claims. Do not collapse them into a single score.

## Handoffs and transition rules

Handoffs name a destination stage and status. `ready` means only that this
record's stated outputs are available for that stage; it is not authorization.
`held` carries blockers and a next action. `not_requested` is a valid standalone
completion. A transition can be proposed without a shared record, but it must
not claim that a downstream stage has occurred.

| From | May hand off to | Required meaning |
|---|---|---|
| create | inspect, evaluate | Candidate and planned cases are identified; no quality claim implied. |
| inspect | evaluate, fix, install, card | Findings are bound to exact bytes; incomplete or adverse findings remain explicit. |
| evaluate | fix, install, card | Conditions, cases, grades, and limitations are retained; inconclusive is not a pass. |
| fix | inspect, evaluate | Predecessor and failing case are retained; changed bytes require fresh relevant evidence. |
| install | card | Preview, applied bytes, and observed discovery/loading are kept distinct. |
| card | none | Summary only; cards do not authorize the next action. |

Installation eligibility is the conjunction of applicable owner authority,
current exact-byte evidence, a collision-free destination, and every required
gate. If the policy or request does not define a gate as applicable, record that
scope decision; the validator does not invent security approval. A stale
fingerprint, unresolved applicable hold, or mismatched predecessor blocks a
`ready` handoff. The install skill remains responsible for authority and
destination checks immediately before applying.

## Standalone fallback

When a protocol record or validator is missing, each skill must still complete
its local workflow and return its existing Markdown template. State which
shared evidence is absent and avoid claims that require it. Do not make a local
tool failure a reason to abandon an otherwise safe read-only task.

## Validation boundaries

`lifecycle.py` validates record shape, enums, digests, predecessor links, and
simple chain consistency. It does not assess instruction quality, run candidate
code, decide whether a scanner is trustworthy, verify a live host load, judge a
task output, or grant authority. Human and specialist decisions remain distinct
evidence with their own scope.


## Version 2 multi-parent records

New records use `schema_version: "panday-skill-lifecycle/v2"`. A parent entry binds `record_id`, identity, and exact fingerprint. Keep review status, evidence status, authority reference, and execution result separate. Validate individual v2 records with `python -B .agents/panday-lifecycle/validate_v2.py <record.json>`; the helper reads data only and never runs candidate code. It validates structure, resolves supplied parent records, verifies exact parent fingerprints, and rejects unresolved parents and cycles. It does not verify external evidence references or certify claims.
