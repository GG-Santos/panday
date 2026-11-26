---
name: issue-triage
description: Review a supplied incident bundle and draft an evidence-linked triage summary.
allowed-tools:
  - Read
  - Grep
  - Glob
model: claude-3-5-sonnet
context: fork
agent: triage-researcher
---

# Issue triage

Use only the supplied incident bundle. Read the [triage rules](references/triage-rules.md), separate confirmed facts from hypotheses, and return a summary with evidence paths. Never change source files or contact a reporter.

