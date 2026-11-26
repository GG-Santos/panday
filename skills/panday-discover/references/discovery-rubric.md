# Candidate discovery rubric

## Search order

1. Search a source or repository the user names.
2. Search the configured local registry.
3. Query the skills.sh catalog when network search is available. The Vercel Skills CLI currently calls `GET https://skills.sh/api/search`; this endpoint is not a documented public API, so Panday treats it as experimental, caches only a bounded result set, and degrades to local sources when it fails. Search can miss valid skills because catalog ingestion and matching are incomplete.
4. For a promising result, inspect its catalog page and retrieve the exact GitHub skill path. A catalog result is a lead, not source verification.

## Matching and ranking

The catalog search uses all query terms first. If fewer than ten exact results appear and the query contains two to six distinct terms, retry with one term omitted at a time; append unique partial results after exact results and cap the merged list at 25. An owner filter narrows the catalog query. This reproduces the current Skills CLI's practical search behavior without installing or executing its npm package.

Rank the shortlist by task and host fit, scope, compatibility, maintenance/provenance evidence, and then popularity as a weak tie-breaker. Record exact URL/repository, observed revision, files actually read, and unknowns. Install counts never establish quality, safety, or suitability. Do not infer that a repository is complete from a search result; prefer a direct exact GitHub tree URL or owner/repo plus skill name when moving to Panday Install.

## Limits

The skills.sh endpoint and index are experimental dependencies and may change or omit valid sources. Report query terms, owner filter, source status, and whether results came from cache. If the catalog is unavailable, use configured paths or user-named GitHub sources; do not report an empty catalog as proof that no skill exists.

## Source references

- Vercel Skills CLI implementation: https://github.com/vercel-labs/skills/blob/main/src/find.ts
- Vercel command guide: https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-find
