"""
Output image resolution logic.

Requirements:
- Input images may live in inputRoot or any subfolder.
- Output images are expected to be inside outputRoot (often flat, may contain subfolders).
- Output filename may add arbitrary prefix/suffix around the input stem:
    e.g. fixed_clothed-142_00001_.png
- Avoid substring collisions:
    "clothed-15" must NOT match "clothed-152"
- If multiple possible outputs exist, pick the newest (mtime).

No Qt dependencies - pure business logic.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List, Set


class OutputResolver:
    """Resolves original images to their generated output images."""

    _IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def __init__(self, outputRoot: Optional[str] = None):
        self.outputRoot: Optional[Path] = Path(outputRoot) if outputRoot else None

    def setOutputRoot(self, outputRoot: str):
        self.outputRoot = Path(outputRoot) if outputRoot else None

    def resolveOutput(self, originalPath: str, inputRoot: Optional[str] = None) -> Optional[str]:
        candidates = self.getPossibleOutputs(originalPath, inputRoot=inputRoot)
        return candidates[0] if candidates else None

    def getPossibleOutputs(self, originalPath: str, inputRoot: Optional[str] = None) -> List[str]:
        outputRoot = self._validatedOutputRoot()
        if outputRoot is None:
            return []

        original = Path(originalPath)
        filename = original.name
        stem = original.stem

        candidates: Set[Path] = set()

        # 1) flat direct: outputRoot / original filename
        direct = outputRoot / filename
        if self._isValidImageFile(direct):
            candidates.add(direct)

        # 2) exact filename anywhere
        for fp in outputRoot.rglob(filename):
            if self._isValidImageFile(fp):
                candidates.add(fp)

        # 3) boundary-aware stem match anywhere (prefix/suffix allowed, but no collisions)
        # e.g. matches "..._clothed-142_..." but not "..._clothed-152_..." for "clothed-15"
        if stem:
            pattern = self._buildStemPattern(stem)
            for fp in outputRoot.rglob("*"):
                if not self._isValidImageFile(fp):
                    continue
                if pattern.search(fp.stem):
                    candidates.add(fp)

        ordered = sorted(candidates, key=self._safeMtime, reverse=True)
        return [str(p) for p in ordered]

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------

    def _validatedOutputRoot(self) -> Optional[Path]:
        if not self.outputRoot:
            return None
        if not self.outputRoot.exists() or not self.outputRoot.is_dir():
            return None
        return self.outputRoot

    def _isValidImageFile(self, path: Path) -> bool:
        try:
            return path.is_file() and path.suffix.lower() in self._IMAGE_EXTS
        except OSError:
            return False

    def _safeMtime(self, path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    def _buildStemPattern(self, stem: str) -> re.Pattern:
        """
        Build a regex that matches stem as a token, not as a substring of a longer token.

        We treat "token chars" as [A-Za-z0-9-] (hyphen is part of your stems).
        Boundaries are start/end or any char NOT in that set (underscore counts as boundary).
        """
        escaped = re.escape(stem)
        return re.compile(rf"(^|[^A-Za-z0-9-]){escaped}($|[^A-Za-z0-9-])")
