"""
Core sidecar file management functionality.
No Qt dependencies - pure business logic.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class SidecarData:
    imagePath: str
    data: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def fromDict(imagePath: str, d: Optional[Dict[str, Any]]) -> "SidecarData":
        return SidecarData(imagePath=imagePath, data=(d or {}))

    def toDict(self) -> Dict[str, Any]:
        return self.data

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

