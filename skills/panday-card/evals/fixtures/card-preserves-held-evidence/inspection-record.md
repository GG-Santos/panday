# Inspection Record IR-17

- Candidate: `candidate/SKILL.md`
- Candidate fingerprint: `sha256:fixture-candidate-17`
- Scope: static review of the supplied `SKILL.md` only
- Security claim: **Held**. A linked script's write destination was not resolved.
- Evidence: `candidate/SKILL.md`, section `## Operation`; review note at this record, section `## Findings`.
- Behavior evaluation: **Not assessed**.
- Owner review: required before any install decision.

## Findings

- `F-1` (medium, held): The skill says it writes a review packet but does not identify a destination boundary. The linked script was not supplied; no code was executed. Do not treat this as a clean security review.
