from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from floodlab.analysis import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FloodLab HW2 analysis pipeline")
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root")
    args = parser.parse_args()
    run(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
