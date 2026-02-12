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
    return imgPath.parent / f"{imgPath.name}.prompt.json"


def loadSidecar(imagePath: str) -> SidecarData:
    """
    Load sidecar data for an image.
    If the sidecar doesn't exist, returns a minimal default.

    Args:
        imagePath: Path to the image file

    Returns:
        SidecarData object
    """
    sidecarPath = getSidecarPath(imagePath)

    if sidecarPath.exists():
        try:
            with open(sidecarPath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SidecarData.fromDict(imagePath, data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load sidecar {sidecarPath}: {e}")

    # Return minimal default
    return SidecarData(imagePath=imagePath)


def saveSidecar(sidecar: SidecarData, createBackup: bool = True):
    """
    Save sidecar data to disk.

    Args:
        sidecar: SidecarData to save
        createBackup: If True, create .bak backup before saving
    """
    sidecarPath = getSidecarPath(sidecar.imagePath)

    # Create backup if file exists
    if createBackup and sidecarPath.exists():
        backupPath = Path(str(sidecarPath) + ".bak")
        try:
            backupPath.write_bytes(sidecarPath.read_bytes())
        except IOError as e:
            print(f"Warning: Could not create backup {backupPath}: {e}")

    # Save the sidecar
    try:
        with open(sidecarPath, "w", encoding="utf-8") as f:
            json.dump(sidecar.toDict(), f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error: Could not save sidecar {sidecarPath}: {e}")
        raise


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
