# Ticket export schema (fixture)

Each row contains `ticket_id`, `created_at`, `region`, `category`, `issue_summary`, `resolution`, and optional `customer_name`.

- `ticket_id` is a stable internal identifier and may be included when a request asks for traceability.
- `customer_name` is personal information and must be omitted from coaching briefs.
- `created_at` is an ISO-8601 date-time. Filter by the user-selected reporting week and state the timezone if supplied.
- `region` is one of North, South, East, or West.
- Empty `resolution` means no resolution was recorded; do not infer one.
