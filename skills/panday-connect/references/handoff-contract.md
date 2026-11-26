# Handoff contract checklist

For each edge define producer and consumer revision, trigger, input artifact/schema, required fields, freshness or fingerprint, validation, data sensitivity, authority boundary, success disposition, held/failed behavior, retry/idempotency, and user-facing fallback. A downstream skill must not infer approval from a prior result. Preserve independent activation and describe partial completion.
