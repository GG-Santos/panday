from pathlib import Path
import json
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import check_package

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
        strict_case=next(case for case in cases if case["id"]=="create-codex-strict-metadata")
        self.assertTrue({"codex","strict-validation","regression","standalone"}.issubset(strict_case["tags"]))
        self.assertTrue({"codex-interface-metadata","strict-target-validation","draft-only"}.issubset({a["id"] for a in strict_case["assertions"]}))
        instructions=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertIn("agents/openai.yaml", instructions)
        self.assertIn("25–64 characters", instructions)
        self.assertIn("strict exit code is zero", instructions)
        self.assertTrue(all(any(a["kind"]=="trigger" for a in c["assertions"]) for c in cases if "routing" in c["tags"]))
        self.assertTrue(all(any(a["kind"]=="safety" for a in c["assertions"]) for c in cases if "boundary" in c["tags"] or "holdout" in c["tags"]))
        for case in cases:
            for filename in case.get("files", []):
                self.assertTrue((ROOT/filename).is_file(), f"missing eval fixture: {filename}")

    def write_valid_candidate(self, root):
        candidate=root/"sample-skill"
        (candidate/"references").mkdir(parents=True)
        (candidate/"evals/fixtures").mkdir(parents=True)
        (candidate/"SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: Handle the sample recurring task.\n---\n"
            "Read [the workflow](references/workflow.md).\n", encoding="utf-8")
        (candidate/"references/workflow.md").write_text("# Workflow\n", encoding="utf-8")
        (candidate/"evals/fixtures/case.md").write_text("sample input\n", encoding="utf-8")
        cases={"version":1,"skill":"sample-skill","scenarios":[
            {"id":"normal-case","prompt":"Handle the sample task.","should_trigger":True,"risk":"low","holdout":False,
             "assertions":[{"id":"result-exists","kind":"outcome","description":"Produces the requested result."}],"files":["evals/fixtures/case.md"]},
            {"id":"near-miss","prompt":"Answer an unrelated question.","should_trigger":False,"risk":"low","holdout":True,
             "assertions":[{"id":"does-not-trigger","kind":"trigger","description":"Does not run the sample workflow."}],"files":[]}
        ]}
        (candidate/"evals/evals.json").write_text(json.dumps(cases), encoding="utf-8")
        return candidate

    def test_data_only_checker_accepts_complete_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate=self.write_valid_candidate(Path(temp))
            result=check_package.validate_package(candidate)
            self.assertTrue(result["passed"], result["findings"])

    def test_data_only_checker_rejects_invalid_eval_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate=self.write_valid_candidate(Path(temp))
            data=json.loads((candidate/"evals/evals.json").read_text(encoding="utf-8"))
            data["scenarios"][0]["risk"]="urgent"
            data["scenarios"][0].pop("holdout")
            data["scenarios"][0]["assertions"]=["not a structured assertion"]
            (candidate/"evals/evals.json").write_text(json.dumps(data), encoding="utf-8")
            result=check_package.validate_package(candidate)
            codes={item["code"] for item in result["findings"]}
            self.assertFalse(result["passed"])
            self.assertTrue({"scenario-risk","scenario-holdout","assertion-type"}.issubset(codes))

    def test_data_only_checker_rejects_missing_links_and_escaping_fixtures(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate=self.write_valid_candidate(Path(temp))
            skill=candidate/"SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8")+"\n[missing](references/not-there.md)\n", encoding="utf-8")
            data=json.loads((candidate/"evals/evals.json").read_text(encoding="utf-8"))
            data["scenarios"][0]["files"].append("../../outside.txt")
            (candidate/"evals/evals.json").write_text(json.dumps(data), encoding="utf-8")
            codes={item["code"] for item in check_package.validate_package(candidate)["findings"]}
            self.assertIn("markdown-link", codes)
            self.assertIn("fixture-escape", codes)

    def test_data_only_checker_never_executes_candidate_scripts(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate=self.write_valid_candidate(Path(temp))
            marker=Path(temp)/"executed.txt"
            scripts=candidate/"scripts"
            scripts.mkdir()
            (scripts/"candidate.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n", encoding="utf-8")
            result=check_package.validate_package(candidate)
            self.assertTrue(result["passed"], result["findings"])
            self.assertFalse(marker.exists())

if __name__ == "__main__": unittest.main()
