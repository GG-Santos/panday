# Panday Skill Governance Card

> Draft for owner review. This card summarizes source evidence; it is not legal approval, security approval, certification, release approval, or proof of task effectiveness.

## Identity

- **Skill name:** {{declared skill name}}
- **Target path:** {{project-relative path}}
- **Project / bundle:** {{project or bundle identity, if known}}
- **Revision or digest:** {{revision, digest and algorithm, or Not available}}
- **Card prepared:** {{date or Not recorded}}
- **Intended reviewer:** {{owner, maintainer, or review group if documented}}

## Purpose and use

- **Declared description:** {{quote the skill frontmatter description}}
- **Purpose:** {{grounded summary}}
- **Intended users and outputs:** {{documented contract or Not documented}}
- **Trigger and exclusions:** {{positive trigger and nearest relevant non-trigger}}

## Operation and boundaries

- **Inputs and prerequisites:** {{documented inputs, environment and dependencies}}
- **Tools and host assumptions:** {{capabilities, availability conditions and fallbacks}}
- **Outputs and write locations:** {{artifacts, destinations and overwrite behavior}}
- **Permissions and side effects:** {{external access, writes, persistence and approvals}}
- **Failure behavior and limits:** {{known gaps, fallbacks and unverified claims}}

## Governance signals

| Field | Finding | Evidence status | Source / uncertainty |
|---|---|---|---|
| Owner / maintainer | {{value or Not documented}} | {{Documented / Observed / Inferred / Not assessed}} | {{relative path and heading or record ID}} |
| License / terms | {{exact declared value or Not documented}} | {{status}} | {{license source; do not infer}} |
| Credentials | {{documented requirement, Not documented, or Not assessed}} | {{status}} | {{source; never include secret values}} |
| Privacy / data handling | {{documented handling or Not assessed}} | {{status}} | {{source and limit}} |
| Portability | {{hosts, platforms and constraints}} | {{status}} | {{source and tested scope}} |

## Risks and safeguards

| Risk or uncertainty | Existing safeguard | Remaining owner action | Evidence |
|---|---|---|---|
| {{specific, supported risk; or None identified in reviewed scope}} | {{documented control or None found}} | {{action or None}} | {{source and scope}} |

## Qualification evidence

Report each category separately. Use `Not assessed` when no current, revision-bound evidence was inspected.

| Claim | Status | Candidate identity and method | Coverage and limitations |
|---|---|---|---|
| Structure / metadata | {{Verified / Failed / Not assessed}} | {{revision, validator or inspection}} | {{checks actually covered}} |
| Package contents | {{Verified / Failed / Not assessed}} | {{archive or inventory evidence}} | {{source-only checks do not establish package contents}} |
| Security review | {{Disposition or Not assessed}} | {{report identity, digest and scope}} | {{scanner and semantic limits}} |
| Host discovery / loading | {{Observed / Failed / Not assessed}} | {{host, exact path and load evidence}} | {{discovery is not task effectiveness}} |
| Task behavior | {{Observed / Failed / Not assessed}} | {{case, baseline, candidate and run record}} | {{sample size, conditions and limits}} |

## Sources and review

- **Reviewed files and records:** {{relative paths, headings, revision-bound report IDs}}
- **External references:** {{direct links and access date, if used}}
- **Unresolved fields:** {{list or None}}
- **Owner review needed:** {{specific confirmation or decision; do not imply approval}}
- **Card status:** Draft / Owner reviewed / Superseded
- **Owner and review date:** {{leave blank until actually supplied}}

When lifecycle records are supplied, cite their IDs and exact fingerprints in
the source/evidence fields. Preserve each original status; the shared protocol
is optional and a card cannot grant approval.
