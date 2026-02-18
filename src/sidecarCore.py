"""
Core sidecar file management functionality.
No Qt dependencies - pure business logic.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SidecarData:
    """Represents a prompt sidecar file."""

    imagePath: str
    prompt: str = ""
    negativePrompt: str = ""
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def toDict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "prompt": self.prompt,
            "negative_prompt": self.negativePrompt,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def fromDict(cls, imagePath: str, data: Dict[str, Any]) -> "SidecarData":
        """Create SidecarData from dictionary."""
        return cls(
            imagePath=imagePath,
            prompt=data.get("prompt", ""),
            negativePrompt=data.get("negative_prompt", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


def getSidecarPath(imagePath: str) -> Path:
    """
    Get the sidecar file path for an image.

    Args:
        imagePath: Path to the image file

    Returns:
        Path to the sidecar file
    """
    imgPath = Path(imagePath)
    # drop extension from image name and add .prompt.json
    baseName = imgPath.stem
    return imgPath.parent / f"{baseName}.prompt.json"


def scanImages(rootPath: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Scan a directory for image files.

    Args:
        rootPath: Root directory to scan
        extensions: List of file extensions to include (default: common image formats)

    Returns:
        List of absolute image file paths
    """
    if extensions is None:
        extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    extensions = [ext.lower() for ext in extensions]
    root = Path(rootPath)

    if not root.exists() or not root.is_dir():
        return []

    images = []
    for filePath in root.rglob("*"):
        if filePath.is_file() and filePath.suffix.lower() in extensions:
            # Skip .prompt.json files
            if ".prompt.json" not in filePath.name:
                images.append(str(filePath.absolute()))

    return sorted(images)


def assemblePrompt(sidecar: SidecarData) -> str:
    """
    Assemble the full prompt text from sidecar data.
    Currently just returns the prompt field, but could be extended
    to include tags or other elements.

    Args:
        sidecar: SidecarData object

    Returns:
        Assembled prompt string
    """
    parts = []

    if sidecar.prompt:
        parts.append(sidecar.prompt)

    if sidecar.tags:
        tagsStr = ", ".join(sidecar.tags)
        parts.append(f"Tags: {tagsStr}")

    return "\n\n".join(parts)
