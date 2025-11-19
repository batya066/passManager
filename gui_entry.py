"""PyInstaller giriş noktası."""

from __future__ import annotations

import sys
from pathlib import Path


def _load_launch():
    try:
        from pass_manager.gui.app import launch as launcher  # type: ignore
        return launcher
    except ModuleNotFoundError:
        project_root = Path(__file__).resolve().parent
        src_path = project_root / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            from pass_manager.gui.app import launch as launcher  # type: ignore

            return launcher
        raise


if __name__ == "__main__":
    _load_launch()()

