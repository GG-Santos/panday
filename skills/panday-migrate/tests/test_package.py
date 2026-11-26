from pathlib import Path
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PackageTests(unittest.TestCase):
    def test_package_contract(self):
        self.assertTrue((ROOT/"SKILL.md").is_file())
        self.assertTrue((ROOT/".skillignore").is_file())
        instructions=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertIn("do not load them for ordinary user tasks", instructions)
        cases=json.loads((ROOT/"evals/evals.json").read_text())["scenarios"]
        self.assertTrue({"normal","routing","failure","boundary","regression","holdout"}.issubset({tag for c in cases for tag in c["tags"]}))
        normal=[case for case in cases if "normal" in case["tags"]]
        self.assertTrue(normal and all("standalone" in case["tags"] for case in normal))
        self.assertTrue(all(any(a["id"]=="task-scoped-resources" and a["kind"]=="process" for a in case["assertions"]) for case in normal))
        self.assertTrue(all(any(a["kind"]=="trigger" for a in c["assertions"]) for c in cases if "routing" in c["tags"]))
        self.assertTrue(all(any(a["kind"]=="safety" for a in c["assertions"]) for c in cases if "boundary" in c["tags"] or "holdout" in c["tags"]))
        for case in cases:
            for filename in case.get("files", []):
                self.assertTrue((ROOT/filename).is_file(), f"missing eval fixture: {filename}")

    def test_claude_to_codex_migration_case_is_complete(self):
        cases=json.loads((ROOT/"evals/evals.json").read_text())["scenarios"]
        case=next((c for c in cases if c["id"]=="migrate-claude-to-codex"), None)
        self.assertIsNotNone(case)
        self.assertTrue(case["should_trigger"])
        self.assertIn("claude-to-codex", case["tags"])
        kinds={a["kind"] for a in case["assertions"]}
        self.assertTrue({"outcome","safety","process"}.issubset(kinds))
        self.assertIn("preserve the source",case["prompt"].lower())
        self.assertIn("do not apply",case["prompt"].lower())
        fixture=ROOT/"evals/fixtures/claude-to-codex/source/.claude/skills/issue-triage"
        self.assertTrue((fixture/"SKILL.md").is_file())
        self.assertTrue((fixture/"references/triage-rules.md").is_file())
        self.assertTrue((ROOT/"evals/fixtures/claude-to-codex/source/.claude/agents/triage-researcher.md").is_file())
        manifest=json.loads((ROOT/"evals/fixtures/claude-to-codex/source/manifest.json").read_text())
        self.assertEqual(manifest["requested_target"],"Codex")
        self.assertEqual(manifest["mode"],"preview-only")

if __name__ == "__main__": unittest.main()
