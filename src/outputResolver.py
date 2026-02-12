"""
Output image resolution logic.
Attempts to find generated/output images corresponding to original images.
No Qt dependencies - pure business logic.
"""

import os
from pathlib import Path
from typing import Optional, List


class OutputResolver:
    """Resolves original images to their generated output images."""

    def __init__(self, outputRoot: Optional[str] = None):
        """
        Initialize the output resolver.

        Args:
            outputRoot: Root directory where output images are stored
        """
        self.outputRoot = Path(outputRoot) if outputRoot else None

    def setOutputRoot(self, outputRoot: str):
        """
        Set or update the output root directory.

        Args:
            outputRoot: Root directory where output images are stored
        """
        self.outputRoot = Path(outputRoot) if outputRoot else None

    def resolveOutput(
        self, originalPath: str, inputRoot: Optional[str] = None
    ) -> Optional[str]:
        """
        Attempt to find the output image for an original image.

        Resolution strategy:
        1. Try same relative path from inputRoot to outputRoot
        2. Try filename match in outputRoot
        3. Try stem-prefix match (e.g., "image" matches "image_001.png")

        Args:
            originalPath: Path to the original image
            inputRoot: Root directory of input images (for relative path calculation)

        Returns:
            Path to output image if found, None otherwise
        """
        if not self.outputRoot or not self.outputRoot.exists():
            return None

        original = Path(originalPath)

        # Strategy 1: Same relative path
        if inputRoot:
            try:
                relPath = original.relative_to(inputRoot)
                outputPath = self.outputRoot / relPath
                if outputPath.exists():
                    return str(outputPath)
            except (ValueError, OSError):
                pass

        # Strategy 2: Filename match
        filenameMatch = self._findByFilename(original.name)
        if filenameMatch:
            return filenameMatch

        # Strategy 3: Stem-prefix match
        stemMatch = self._findByStemPrefix(original.stem)
        if stemMatch:
            return stemMatch

        return None

    def _findByFilename(self, filename: str) -> Optional[str]:
        """
        Find a file with exact filename match in output_root.

        Args:
            filename: Filename to search for

        Returns:
            Path to matching file if found, None otherwise
        """
        if not self.outputRoot:
            return None

        for filePath in self.outputRoot.rglob(filename):
            if filePath.is_file():
                return str(filePath)

        return None

    def _findByStemPrefix(self, stem: str) -> Optional[str]:
        """
        Find a file whose stem starts with the given stem.
        E.g., "image" matches "image_001.png", "image_final.jpg"

        Args:
            stem: Filename stem to match as prefix

        Returns:
            Path to first matching file if found, None otherwise
        """
        if not self.outputRoot:
            return None

        # Common image extensions to check
        extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

        for filePath in self.outputRoot.rglob("*"):
            if filePath.is_file():
                if (
                    filePath.stem.startswith(stem)
                    and filePath.suffix.lower() in extensions
                ):
                    return str(filePath)

        return None

    def getPossibleOutputs(
        self, originalPath: str, inputRoot: Optional[str] = None
    ) -> List[str]:
        """
        Get all possible output images for an original image.
        Useful for debugging or presenting multiple options to the user.

        Args:
            originalPath: Path to the original image
            inputRoot: Root directory of input images

        Returns:
            List of possible output image paths
        """
        if not self.outputRoot or not self.outputRoot.exists():
            return []

        original = Path(originalPath)
        results = []

        # Collect all candidates
        candidates = set()

        # From relative path
        if inputRoot:
            try:
                relPath = original.relative_to(inputRoot)
                outputPath = self.outputRoot / relPath
                if outputPath.exists():
                    candidates.add(str(outputPath))
            except (ValueError, OSError):
                pass

        # From filename matches
        for filePath in self.outputRoot.rglob(original.name):
            if filePath.is_file():
                candidates.add(str(filePath))

        # From stem-prefix matches
        extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        for filePath in self.outputRoot.rglob("*"):
            if filePath.is_file():
                if (
                    filePath.stem.startswith(original.stem)
                    and filePath.suffix.lower() in extensions
                ):
                    candidates.add(str(filePath))

        return sorted(list(candidates))
