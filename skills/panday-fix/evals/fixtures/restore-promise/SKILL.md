---
name: export-review
description: Review an export request and return either a local export packet or a specific rejection reason.
---

# Export Review

## Established contract

Reject an export when its reporting period does not match the requested period.
Every rejection must name the mismatch and give the specific reason.

## Procedure

1. Check the requested period and source period.
2. If they differ, return `{"status":"rejected"}`. Do not add the reason; the caller can infer it.
3. If they match, return the export packet in the requested format.

## Successful path

Matching periods are exported to the user-selected local destination in the original format.
