"""Data-only package structure check; never imports candidate scripts."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
required=("SKILL.md",)
missing=[name for name in required if not (root/name).is_file()]
print("package structure: " + ("OK" if not missing else "MISSING " + ", ".join(missing)))
raise SystemExit(bool(missing))
