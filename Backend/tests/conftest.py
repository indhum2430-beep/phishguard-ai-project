import sys
from pathlib import Path

# Make detector.py and app.py (one folder up) importable from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))