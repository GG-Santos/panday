---
name: invoice-check
description: Reconcile a supplier invoice against its purchase order and flag mismatches. Use for invoice-to-order checks.
---

# Invoice Check

1. Read the invoice and purchase order supplied for this request.
2. Compare supplier, currency, line descriptions, quantities, unit prices, and totals.
3. Return a table of matching and mismatched fields with source references.
4. Do not approve payment, change accounting records, or infer missing values.

The current task asks to add support for credit notes while preserving ordinary invoice checks.
