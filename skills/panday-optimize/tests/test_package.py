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
        instructions=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Resource scope", instructions)
        self.assertIn("Do not read this package's own `evals/`, `tests/`, `scripts/`", instructions)
        self.assertIn("only when the user asks to create, edit, inspect, or validate the Panday Optimize package", instructions)
        cases=json.loads((ROOT/"evals/evals.json").read_text())["scenarios"]
        self.assertTrue({"normal","routing","failure","boundary","regression","holdout"}.issubset({tag for c in cases for tag in c["tags"]}))
        normal=[case for case in cases if "normal" in case["tags"]]
        self.assertTrue(normal and all("standalone" in case["tags"] for case in normal))
        self.assertTrue(any(a.get("id")=="task-scoped-resources" and a.get("kind")=="process" and "run trace" in a.get("description","") for case in normal for a in case["assertions"]))
        self.assertTrue(all(any(a["kind"]=="trigger" for a in c["assertions"]) for c in cases if "routing" in c["tags"]))
        self.assertTrue(all(any(a["kind"]=="safety" for a in c["assertions"]) for c in cases if "boundary" in c["tags"] or "holdout" in c["tags"]))
        for case in cases:
            for filename in case.get("files", []):
                self.assertTrue((ROOT/filename).is_file(), f"missing eval fixture: {filename}")
if __name__ == "__main__": unittest.main()
