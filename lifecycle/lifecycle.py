#!/usr/bin/env python3
"""Validate Panday lifecycle evidence without executing candidate content."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "habi-skill-lifecycle/v1"
ALGORITHM = "sha256-tree-v1"
TYPES = {"create", "inspect", "evaluate", "fix", "install", "card"}
STATUSES = {"verified", "failed", "observed", "held", "unassessed"}
TRANSITIONS = {
    "create": {"inspect", "evaluate"},
    "inspect": {"evaluate", "fix", "install", "card"},
    "evaluate": {"fix", "install", "card"},
    "fix": {"inspect", "evaluate"},
    "install": {"card"},
    "card": set(),
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(ValueError):
    pass


def fingerprint(path: Path) -> dict[str, Any]:
    """Hash regular files and their relative paths in a stable order."""
    if path.is_symlink():
        raise ValidationError(f"candidate root cannot be a symbolic link: {path}")
    root = path.resolve(strict=True)
    if not root.is_dir():
        raise ValidationError(f"candidate must be a directory: {path}")
    files: list[Path] = []
    for item in root.rglob("*"):
        if item.is_symlink():
            raise ValidationError(f"symbolic links are not supported: {item.relative_to(root)}")
        if item.is_file():
            files.append(item)
        elif not item.is_dir():
            raise ValidationError(f"unsupported filesystem entry: {item.relative_to(root)}")
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    digest = hashlib.sha256()
    total_bytes = 0
    for item in files:
        relative = item.relative_to(root).as_posix().encode("utf-8")
        content_hash = hashlib.sha256()
        size = 0
        with item.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                size += len(chunk)
                content_hash.update(chunk)
        total_bytes += size
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(size.to_bytes(8, "big"))
        digest.update(content_hash.digest())
    return {
        "algorithm": ALGORITHM,
        "digest": digest.hexdigest(),
        "file_count": len(files),
        "byte_count": total_bytes,
    }


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_record(record: Any) -> dict[str, Any]:
    """Check the protocol's required cross-field invariants."""
    _need(isinstance(record, dict), "record must be a JSON object")
    for key in ("schema", "record_id", "record_type", "created_at", "subject", "scope", "claims", "findings", "lineage", "handoff"):
        _need(key in record, f"missing required field: {key}")
    _need(record["schema"] == SCHEMA, f"schema must be {SCHEMA}")
    _need(_text(record["record_id"]), "record_id must be a non-empty string")
    _need(isinstance(record["record_type"], str) and record["record_type"] in TYPES, "record_type is not supported")
    try:
        timestamp = dt.datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValidationError("created_at must be an ISO-8601 timestamp") from exc
    _need(timestamp.tzinfo is not None, "created_at must include a timezone")

    subject = record["subject"]
    _need(isinstance(subject, dict), "subject must be an object")
    _need(_text(subject.get("name")), "subject.name must be non-empty")
    _need(_text(subject.get("source_path")), "subject.source_path must be non-empty")
    fp = subject.get("fingerprint")
    _need(isinstance(fp, dict), "subject.fingerprint must be an object")
    _need(fp.get("algorithm") == ALGORITHM, f"fingerprint algorithm must be {ALGORITHM}")
    _need(isinstance(fp.get("digest"), str) and HEX64.fullmatch(fp["digest"]) is not None, "fingerprint.digest must be a lowercase SHA-256 hex digest")
    for key in ("file_count", "byte_count"):
        _need(isinstance(fp.get(key), int) and not isinstance(fp.get(key), bool) and fp[key] >= 0, f"fingerprint.{key} must be a non-negative integer")

    scope = record["scope"]
    _need(isinstance(scope, dict) and _text(scope.get("purpose")) and _text(scope.get("authority")), "scope requires purpose and authority")
    _need(isinstance(scope.get("project", ""), str), "scope.project must be a string")
    claims = record["claims"]
    _need(isinstance(claims, list), "claims must be an array")
    claim_ids: set[str] = set()
    for claim in claims:
        _need(isinstance(claim, dict), "each claim must be an object")
        _need(_text(claim.get("claim_id")) and claim["claim_id"] not in claim_ids, "claim_id values must be non-empty and unique")
        claim_ids.add(claim["claim_id"])
        _need(isinstance(claim.get("status"), str) and claim["status"] in STATUSES, f"unsupported status for claim {claim.get('claim_id')}")
        _need(_text(claim.get("method")), f"claim {claim['claim_id']} needs a method")
        _need(isinstance(claim.get("evidence"), list), f"claim {claim['claim_id']} evidence must be an array")
        _need(isinstance(claim.get("coverage"), str), f"claim {claim['claim_id']} coverage must be a string")
        _need(isinstance(claim.get("limitations"), list) and all(isinstance(item, str) for item in claim["limitations"]), f"claim {claim['claim_id']} limitations must be strings")
        if claim["status"] in {"verified", "failed", "observed"}:
            _need(bool(claim["evidence"]), f"claim {claim['claim_id']} needs evidence for status {claim['status']}")
        if claim["status"] == "held":
            _need(bool(claim["limitations"]), f"held claim {claim['claim_id']} must explain the blocker in limitations")
        for evidence in claim["evidence"]:
            _need(isinstance(evidence, dict) and _text(evidence.get("source")) and _text(evidence.get("description")), f"claim {claim['claim_id']} has invalid evidence")

    findings = record["findings"]
    _need(isinstance(findings, list), "findings must be an array")
    finding_ids: set[str] = set()
    for finding in findings:
        _need(isinstance(finding, dict), "each finding must be an object")
        _need(_text(finding.get("finding_id")) and finding["finding_id"] not in finding_ids, "finding_id values must be non-empty and unique")
        finding_ids.add(finding["finding_id"])
        _need(_text(finding.get("claim_id")) and finding["claim_id"] in claim_ids, "finding must reference a declared claim")
        _need(isinstance(finding.get("severity"), str) and finding["severity"] in {"info", "low", "medium", "high", "critical"}, "finding severity is invalid")
        _need(isinstance(finding.get("disposition"), str) and finding["disposition"] in {"open", "resolved", "accepted", "not_applicable"}, "finding disposition is invalid")
        _need(_text(finding.get("summary")) and isinstance(finding.get("evidence"), list), "finding needs a summary and evidence list")
        for evidence in finding["evidence"]:
            _need(isinstance(evidence, dict) and _text(evidence.get("source")) and _text(evidence.get("description")), f"finding {finding['finding_id']} has invalid evidence")

    lineage = record["lineage"]
    _need(isinstance(lineage, dict), "lineage must be an object")
    predecessors = lineage.get("predecessor_record_ids")
    _need(isinstance(predecessors, list) and all(_text(item) for item in predecessors), "lineage.predecessor_record_ids must be strings")
    _need(len(set(predecessors)) == len(predecessors), "predecessor record IDs must be unique")
    parent = lineage.get("parent_digest")
    _need(parent is None or (isinstance(parent, str) and HEX64.fullmatch(parent) is not None), "lineage.parent_digest must be null or a SHA-256 digest")

    handoff = record["handoff"]
    _need(isinstance(handoff, dict), "handoff must be an object")
    destination = handoff.get("to")
    _need(destination is None or (isinstance(destination, str) and destination in TYPES), "handoff.to is invalid")
    status = handoff.get("status")
    _need(isinstance(status, str) and status in {"ready", "held", "not_requested"}, "handoff.status is invalid")
    blockers = handoff.get("blockers")
    _need(isinstance(blockers, list) and all(_text(item) for item in blockers), "handoff.blockers must be non-empty strings")
    _need(isinstance(handoff.get("next_action"), str), "handoff.next_action must be a string")
    if status == "held":
        _need(bool(blockers), "a held handoff must name at least one blocker")
    if status == "ready":
        _need(destination is not None, "a ready handoff must name its destination")
        _need(not blockers, "a ready handoff cannot contain blockers")
        _need(destination in TRANSITIONS[record["record_type"]], "handoff destination is not permitted for this record type")
        _need(not any(claim["status"] == "held" for claim in claims), "a ready handoff cannot contain held claims")
        if any(claim["status"] == "failed" for claim in claims):
            _need(destination in {"fix", "card"}, "failed claims may hand off only to Fix Skill or Card Skill")
        if destination == "install":
            _need(not any(claim["status"] == "failed" for claim in claims), "failed claims cannot hand off ready to Install Skill")
            _need(not any(f["severity"] in {"high", "critical"} and f["disposition"] == "open" for f in findings), "Install Skill cannot receive a ready record with open high or critical findings")
        if destination == "install":
            required = record.get("metadata", {}).get("installation_gates") if isinstance(record.get("metadata", {}), dict) else None
            _need(isinstance(required, list) and bool(required) and all(_text(item) for item in required), "ready-to-install requires metadata.installation_gates to list the applicable verified claim IDs")
            _need(len(set(required)) == len(required), "installation_gates must not contain duplicates")
            _need(all(item in claim_ids for item in required), "installation_gates must reference declared claim IDs")
            _need(all(next(claim for claim in claims if claim["claim_id"] == item)["status"] == "verified" for item in required), "every applicable installation gate must be verified")
    if status == "not_requested":
        _need(destination is None, "not_requested handoff must set to null")
    _need(record["record_type"] != "card" or status != "ready", "a card is a terminal summary and cannot authorize another stage")
    if "metadata" in record:
        _need(isinstance(record["metadata"], dict), "metadata must be an object")
    return record


def load_record(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON record {path}: {exc}") from exc
    return validate_record(value)


def validate_chain(paths: list[Path]) -> list[dict[str, Any]]:
    records = [load_record(path) for path in paths]
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        if record["record_id"] in by_id:
            raise ValidationError(f"duplicate record_id: {record['record_id']}")
        by_id[record["record_id"]] = record
    for record in records:
        for predecessor_id in record["lineage"]["predecessor_record_ids"]:
            predecessor = by_id.get(predecessor_id)
            if predecessor is None:
                raise ValidationError(f"unresolved predecessor {predecessor_id!r} for {record['record_id']}")
            if predecessor["record_type"] not in TRANSITIONS or record["record_type"] not in TRANSITIONS[predecessor["record_type"]]:
                raise ValidationError(f"invalid transition {predecessor['record_type']} -> {record['record_type']}")
            if predecessor["subject"]["name"] != record["subject"]["name"]:
                raise ValidationError(f"subject name changed across predecessor {predecessor_id}; use a new lifecycle identity")
            previous_digest = predecessor["subject"]["fingerprint"]["digest"]
            current_digest = record["subject"]["fingerprint"]["digest"]
            if previous_digest != current_digest and record["lineage"].get("parent_digest") != previous_digest:
                raise ValidationError(f"changed candidate in {record['record_id']} must bind parent_digest to predecessor {predecessor_id}")
            if predecessor["handoff"]["status"] != "ready" or predecessor["handoff"]["to"] != record["record_type"]:
                raise ValidationError(f"predecessor {predecessor_id} did not hand off ready to {record['record_type']}")
    return records


def _emit(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {item}")
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fp_parser = sub.add_parser("fingerprint", help="hash a skill directory without executing its contents")
    fp_parser.add_argument("path", type=Path)
    fp_parser.add_argument("--json", action="store_true")
    record_parser = sub.add_parser("validate-record", help="validate one lifecycle record")
    record_parser.add_argument("record", type=Path)
    record_parser.add_argument("--candidate", type=Path, help="also compare the record fingerprint to this directory")
    record_parser.add_argument("--json", action="store_true")
    chain_parser = sub.add_parser("validate-chain", help="validate records and their explicit handoffs")
    chain_parser.add_argument("records", nargs="+", type=Path)
    chain_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "fingerprint":
            result = fingerprint(args.path)
        elif args.command == "validate-record":
            result = load_record(args.record)
            if args.candidate:
                actual = fingerprint(args.candidate)
                expected = result["subject"]["fingerprint"]
                if actual != expected:
                    raise ValidationError("candidate fingerprint does not match record subject")
            result = {"valid": True, "record_id": result["record_id"], "record_type": result["record_type"], "subject_digest": result["subject"]["fingerprint"]["digest"]}
        else:
            records = validate_chain(args.records)
            result = {"valid": True, "record_count": len(records), "record_ids": [r["record_id"] for r in records]}
        _emit(result, args.json)
        return 0
    except ValidationError as exc:
        _emit({"valid": False, "error": str(exc)}, getattr(args, "json", False))
        return 2
    except OSError as exc:
        _emit({"valid": False, "error": str(exc)}, getattr(args, "json", False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
