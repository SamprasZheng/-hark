import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: read_file.py PATH")

path = Path(sys.argv[1])
sys.stdout.write(path.read_text(encoding="utf-8"))
