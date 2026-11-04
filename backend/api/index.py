import sys
from pathlib import Path

# Thêm root của backend vào sys.path để import được src.*
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.main import app

__all__ = ["app"]
