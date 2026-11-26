# Codex and Claude provider mapping

## Shared contract

Both providers use a folder containing a `SKILL.md` with YAML frontmatter fields `name` and `description`. Preserve instruction text and linked resources unless the owner accepts a specific transformation. Do not confuse a package layout conversion with successful activation in the target host.

## Codex target

Place project skills under `.agents/skills/<name>/`. Codex can display optional interface metadata in `agents/openai.yaml`; when absent, Panday can derive `display_name`, a bounded `short_description`, and `default_prompt` from the skill manifest. Preserve source instructions and resources. Validate the target name, frontmatter, local links, and metadata file structure.

## Claude target

Place project skills under `.claude/skills/<name>/`. Claude requires `name` and `description`; names are at most 64 characters, lowercase letters/numbers/hyphens, and cannot contain `anthropic` or `claude`. Descriptions are non-empty and at most 1,024 characters; XML tags are prohibited. Preserve unrelated provider metadata as inert source files and disclose it in the report instead of silently deleting it.

## Required migration map

For each source file, classify it as preserved, transformed, unsupported, or owner decision. Record source provider/revision, target provider, source and target fingerprints, output path, warnings, and target checks. Codex-to-Claude currently checks Claude manifest constraints and flags Codex interface metadata as inert. Claude-to-Codex creates `agents/openai.yaml` when absent. Host-specific tools, permissions, activation behavior, and external integrations remain manual review unless an explicit mapping exists.

Panday CLI performs local packaging checks and this bounded metadata mapping. It does not run either host, certify activation, or prove behavioral equivalence.

## Target format references

- OpenAI skill package guidance: https://developers.openai.com/plugins/concepts/skills
- Anthropic Agent Skills overview and frontmatter rules: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
