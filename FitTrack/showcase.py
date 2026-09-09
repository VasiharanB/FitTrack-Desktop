"""
showcase.py (Forwarder)
=======================
Convenience launcher to run showcase.py from inside the FitTrack directory.
"""
import sys
import subprocess
from pathlib import Path

root_showcase = Path(__file__).resolve().parent.parent / "showcase.py"
if root_showcase.exists():
    raise SystemExit(subprocess.run([sys.executable, str(root_showcase)], cwd=str(root_showcase.parent)).returncode)
else:
    sys.exit(f"Error: Could not locate root showcase.py at {root_showcase}")
