"""Copy the rendered entry image to the make.fun output directory.

Standard library only. Reads entry.png beside this file and writes it to
/output/entry.png, or to $MAKEFUN_OUTPUT_DIR/entry.png when that is set
(for local runs: MAKEFUN_OUTPUT_DIR=out python3 main.py).
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
DEST_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
DEST = DEST_DIR / "entry.png"


def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DEST)
    print(f"copied {SRC} -> {DEST} ({DEST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
