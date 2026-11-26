import yaml
import shutil
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])
shutil.copyfile(source, output)
Path("../../shared/last-run.txt").write_text("updated")
