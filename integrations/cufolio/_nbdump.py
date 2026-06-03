"""Dump code cells of a Jupyter notebook to stdout (helper for reading cuFOLIO
example notebooks without nested-quote escaping). Usage: python _nbdump.py nb.ipynb"""
import json
import sys

nb = json.load(open(sys.argv[1], encoding="utf-8"))
for i, c in enumerate(nb.get("cells", [])):
    if c.get("cell_type") == "code":
        src = "".join(c.get("source", [])).strip()
        if src:
            print(f"\n# ===== code cell {i} =====")
            print(src)
