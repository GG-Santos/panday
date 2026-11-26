import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "lifecycle.py"
spec = importlib.util.spec_from_file_location("habi_lifecycle", MODULE_PATH)
lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lifecycle)


def make_record(root: Path, record_id="r1", kind="create", to="inspect", status="ready", digest=None, predecessors=None, parent=None):
    fp = lifecycle.fingerprint(root)
    if digest:
        fp["digest"] = digest
    return {
        "schema": lifecycle.SCHEMA,
        "record_id": record_id,
        "record_type": kind,
        "created_at": "2026-11-23T00:00:00Z",
        "subject": {"name": "example", "source_path": "skills/example", "fingerprint": fp},
        "scope": {"project": "demo", "purpose": "test protocol", "authority": "read-only"},
        "claims": [{"claim_id": "structure", "status": "verified", "method": "unit test", "evidence": [{"source": "test", "description": "passed"}], "coverage": "one fixture", "limitations": []}],
        "findings": [],
        "lineage": {"predecessor_record_ids": predecessors or [], "parent_digest": parent},
        "handoff": {"to": to, "status": status, "blockers": [], "next_action": "continue"},
    }


class FingerprintTests(unittest.TestCase):
    def test_fingerprint_is_stable_and_content_sensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            first = lifecycle.fingerprint(root)
            self.assertEqual(first, lifecycle.fingerprint(root))
            (root / "a.txt").write_text("beta", encoding="utf-8")
            self.assertNotEqual(first["digest"], lifecycle.fingerprint(root)["digest"])

    def test_candidate_code_is_never_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            root.mkdir()
            sentinel = Path(tmp) / "executed.txt"
            (root / "helper.py").write_text(
                f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('ran')\n",
                encoding="utf-8",
            )
            lifecycle.fingerprint(root)
            self.assertFalse(sentinel.exists())

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            target = root / "candidate"
            target.mkdir()
            try:
                (target / "link.txt").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(lifecycle.ValidationError):
                lifecycle.fingerprint(target)


class RecordTests(unittest.TestCase):
    def test_valid_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("example", encoding="utf-8")
            self.assertEqual("r1", lifecycle.validate_record(make_record(root))["record_id"])

    def test_malformed_enum_types_return_validation_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for field, value in (("record_type", []), ("handoff", {"to": [], "status": "ready", "blockers": [], "next_action": ""})):
                record = make_record(root)
                if field == "record_type":
                    record[field] = value
                else:
                    record[field] = value
                with self.subTest(field=field), self.assertRaises(lifecycle.ValidationError):
                    lifecycle.validate_record(record)

    def test_held_handoff_requires_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = make_record(root, status="held")
            with self.assertRaisesRegex(lifecycle.ValidationError, "blocker"):
                lifecycle.validate_record(record)

    def test_failed_claim_can_handoff_to_fix_but_not_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = make_record(root, kind="evaluate", to="fix")
            record["claims"][0]["status"] = "failed"
            self.assertEqual("r1", lifecycle.validate_record(record)["record_id"])
            record["handoff"]["to"] = "install"
            record["metadata"] = {"installation_gates": ["structure"]}
            with self.assertRaisesRegex(lifecycle.ValidationError, "failed claims"):
                lifecycle.validate_record(record)

    def test_install_requires_verified_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = make_record(root, kind="inspect", to="install")
            with self.assertRaisesRegex(lifecycle.ValidationError, "installation_gates"):
                lifecycle.validate_record(record)
            record["metadata"] = {"installation_gates": ["structure"]}
            self.assertEqual("r1", lifecycle.validate_record(record)["record_id"])

    def test_changed_tree_requires_parent_digest_and_correct_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("v1", encoding="utf-8")
            prior = make_record(root, "inspect-1", "inspect", "fix")
            old_digest = prior["subject"]["fingerprint"]["digest"]
            (root / "SKILL.md").write_text("v2", encoding="utf-8")
            repaired = make_record(root, "fix-1", "fix", "inspect", predecessors=["inspect-1"], parent=old_digest)
            with tempfile.TemporaryDirectory() as records_dir:
                first = Path(records_dir) / "inspect.json"
                second = Path(records_dir) / "fix.json"
                first.write_text(json.dumps(prior), encoding="utf-8")
                second.write_text(json.dumps(repaired), encoding="utf-8")
                self.assertEqual(2, len(lifecycle.validate_chain([first, second])))
                repaired["lineage"]["parent_digest"] = None
                second.write_text(json.dumps(repaired), encoding="utf-8")
                with self.assertRaisesRegex(lifecycle.ValidationError, "parent_digest"):
                    lifecycle.validate_chain([first, second])

    def test_chain_rejects_subject_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior = make_record(root, "create-1", "create", "inspect")
            current = make_record(root, "inspect-1", "inspect", "card", predecessors=["create-1"])
            current["subject"]["name"] = "renamed-skill"
            with tempfile.TemporaryDirectory() as records_dir:
                first = Path(records_dir) / "create.json"
                second = Path(records_dir) / "inspect.json"
                first.write_text(json.dumps(prior), encoding="utf-8")
                second.write_text(json.dumps(current), encoding="utf-8")
                with self.assertRaisesRegex(lifecycle.ValidationError, "subject name"):
                    lifecycle.validate_chain([first, second])

    def test_full_lifecycle_handoff_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("stable", encoding="utf-8")
            records = []
            transitions = [
                ("create", "inspect"),
                ("inspect", "evaluate"),
                ("evaluate", "fix"),
                ("fix", "inspect"),
                ("inspect", "install"),
                ("install", "card"),
            ]
            previous = None
            for index, (kind, destination) in enumerate(transitions, 1):
                record = make_record(root, f"step-{index}", kind, destination, predecessors=[previous] if previous else [])
                if destination == "install":
                    record["metadata"] = {"installation_gates": ["structure"]}
                records.append(record)
                previous = record["record_id"]
            records.append(make_record(root, "step-7", "card", None, status="not_requested", predecessors=[previous]))
            with tempfile.TemporaryDirectory() as records_dir:
                paths=[]
                for record in records:
                    path=Path(records_dir) / f"{record['record_id']}.json"
                    path.write_text(json.dumps(record), encoding="utf-8")
                    paths.append(path)
                self.assertEqual(7, len(lifecycle.validate_chain(paths)))


if __name__ == "__main__":
    unittest.main()
