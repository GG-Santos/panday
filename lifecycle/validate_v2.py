"""Data-only validation for Panday Lifecycle v2 records."""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "panday-skill-lifecycle/v2"
HEX = re.compile(r"^[0-9a-f]{64}$")
OPS = {"discover", "create", "inspect", "evaluate", "fix", "install", "card", "augment", "synthesize", "optimize", "connect", "migrate"}
STATUSES = {"verified", "failed", "observed", "held", "unassessed"}


class InvalidRecord(ValueError):
    pass


def validate(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise InvalidRecord("record must be an object")
    required = {"schema_version", "record_id", "operation", "subject", "parents", "source_snapshot", "input_fingerprint", "evidence", "compatibility", "review_status", "authority_reference", "created_at", "tool_version"}
    missing = required - record.keys()
    if missing:
        raise InvalidRecord(f"missing fields: {', '.join(sorted(missing))}")
    if record["schema_version"] != SCHEMA or record["operation"] not in OPS:
        raise InvalidRecord("unsupported schema version or operation")
    if not isinstance(record["record_id"], str) or not record["record_id"].strip():
        raise InvalidRecord("record_id must be non-empty")
    if not isinstance(record["subject"], dict) or not isinstance(record["subject"].get("identity"), str):
        raise InvalidRecord("subject.identity is required")
    def check_fp(fp: Any, label: str) -> None:
        if not isinstance(fp, dict) or not isinstance(fp.get("algorithm"), str) or not HEX.fullmatch(str(fp.get("digest", ""))):
            raise InvalidRecord(f"{label} must contain an algorithm and lowercase SHA-256 digest")
    check_fp(record["subject"].get("fingerprint"), "subject.fingerprint")
    check_fp(record["source_snapshot"], "source_snapshot")
    check_fp(record["input_fingerprint"], "input_fingerprint")
    if record.get("output_fingerprint") is not None:
        check_fp(record["output_fingerprint"], "output_fingerprint")
    parents = record["parents"]
    if not isinstance(parents, list):
        raise InvalidRecord("parents must be an array")
    seen: set[str] = set()
    for parent in parents:
        if not isinstance(parent, dict) or not all(isinstance(parent.get(k), str) and parent[k].strip() for k in ("record_id", "identity")):
            raise InvalidRecord("each parent needs record_id and identity")
        if parent["record_id"] in seen:
            raise InvalidRecord("duplicate parent record_id")
        seen.add(parent["record_id"])
        check_fp(parent.get("fingerprint"), "parent.fingerprint")
    evidence = record["evidence"]
    if not isinstance(evidence, list):
        raise InvalidRecord("evidence must be an array")
    for item in evidence:
        if not isinstance(item, dict) or item.get("status") not in STATUSES or not isinstance(item.get("claim"), str) or not item["claim"].strip() or not isinstance(item.get("method"), str) or not item["method"].strip() or not isinstance(item.get("limitations"), list):
            raise InvalidRecord("evidence item requires claim, supported status, method, and limitations")
    if record["review_status"] not in {"reviewed", "held", "not_reviewed", "rejected"}:
        raise InvalidRecord("invalid review_status")
    if not isinstance(record["compatibility"], dict):
        raise InvalidRecord("compatibility must be an object")
    if record["review_status"] == "held" and not any(e.get("status") == "held" for e in evidence):
        raise InvalidRecord("held review requires held evidence")
    try:
        stamp = dt.datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError, TypeError) as exc:
        raise InvalidRecord("created_at must be ISO-8601") from exc
    if stamp.tzinfo is None:
        raise InvalidRecord("created_at must include a timezone")
    if not isinstance(record["tool_version"], str) or not record["tool_version"].strip():
        raise InvalidRecord("tool_version must be non-empty")
    # Authority is intentionally validated as a separate reference, never inferred from review_status.
    if record["authority_reference"] is not None and not isinstance(record["authority_reference"], str):
        raise InvalidRecord("authority_reference must be a string or null")
    return record


def validate_chain(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate a supplied v2 record set and resolve every parent fingerprint."""
    checked=[validate(record) for record in records]
    by_id={}
    for record in checked:
        rid=record["record_id"]
        if rid in by_id: raise InvalidRecord(f"duplicate record_id: {rid}")
        by_id[rid]=record
    graph={rid:[] for rid in by_id}
    for record in checked:
        rid=record["record_id"]
        for parent in record["parents"]:
            source=by_id.get(parent["record_id"])
            if source is None: raise InvalidRecord(f"unresolved parent {parent['record_id']!r} for {rid}")
            if source["subject"]["identity"]!=parent["identity"]:
                raise InvalidRecord(f"parent identity mismatch for {parent['record_id']!r}")
            expected=source.get("output_fingerprint") or source["subject"]["fingerprint"]
            if expected!=parent["fingerprint"]:
                raise InvalidRecord(f"stale parent fingerprint for {parent['record_id']!r}")
            graph[rid].append(parent["record_id"])
    visiting=set(); visited=set()
    def visit(node: str) -> None:
        if node in visiting: raise InvalidRecord("parent references contain a cycle")
        if node in visited: return
        visiting.add(node)
        for parent in graph[node]: visit(parent)
        visiting.remove(node); visited.add(node)
    for node in graph: visit(node)
    return checked


def main() -> int:
    try:
        record = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        validate(record)
        print(json.dumps({"ok": True, "schema": SCHEMA, "approval_granted": False}))
        return 0
    except (OSError, json.JSONDecodeError, IndexError, InvalidRecord) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "approval_granted": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
