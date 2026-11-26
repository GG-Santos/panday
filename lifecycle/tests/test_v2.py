import importlib.util
import unittest
from pathlib import Path

SPEC=importlib.util.spec_from_file_location("panday_v2",Path(__file__).parents[1]/"validate_v2.py")
module=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(module)

def fp(): return {"algorithm":"sha256-tree-v1","digest":"a"*64}
def record():
    return {"schema_version":module.SCHEMA,"record_id":"r2","operation":"synthesize","subject":{"identity":"merged","fingerprint":fp()},"parents":[{"record_id":"a","identity":"first","fingerprint":fp()},{"record_id":"b","identity":"second","fingerprint":fp()}],"source_snapshot":fp(),"input_fingerprint":fp(),"output_fingerprint":None,"evidence":[{"claim":"structure","status":"verified","method":"strict validator","coverage":"package","limitations":[]}],"compatibility":{},"review_status":"reviewed","authority_reference":None,"created_at":"2026-11-24T00:00:00Z","tool_version":"0.1.0"}

class V2Tests(unittest.TestCase):
    def test_multi_parent_record(self): self.assertEqual(len(module.validate(record())["parents"]),2)
    def test_rejects_duplicate_parent_identity_record(self):
        item=record(); item["parents"][1]["record_id"]="a"
        with self.assertRaises(module.InvalidRecord): module.validate(item)
    def test_hold_is_not_an_authorization(self):
        item=record(); item["review_status"]="held"
        with self.assertRaises(module.InvalidRecord): module.validate(item)
    def test_chain_checks_each_parent_fingerprint(self):
        first=record(); first["record_id"]="a"; first["operation"]="create"; first["subject"]["identity"]="first"; first["parents"]=[]
        second=record(); second["record_id"]="b"; second["operation"]="augment"; second["subject"]["identity"]="second"; second["parents"]=[{"record_id":"a","identity":"first","fingerprint":fp()}]
        self.assertEqual(len(module.validate_chain([first,second])),2)
        second["parents"][0]["fingerprint"]["digest"]="b"*64
        with self.assertRaises(module.InvalidRecord): module.validate_chain([first,second])

if __name__ == "__main__": unittest.main()
