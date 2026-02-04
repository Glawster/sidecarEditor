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
    
    image_path: str
    prompt: str = ""
    negative_prompt: str = ""
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, image_path: str, data: Dict[str, Any]) -> 'SidecarData':
        """Create SidecarData from dictionary."""
        return cls(
            image_path=image_path,
            prompt=data.get('prompt', ''),
            negative_prompt=data.get('negative_prompt', ''),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )


def get_sidecar_path(image_path: str) -> Path:
    """
    Get the sidecar file path for an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Path to the sidecar file
    """
    img_path = Path(image_path)
    return img_path.parent / f"{img_path.name}.prompt.json"


def load_sidecar(image_path: str) -> SidecarData:
    """
    Load sidecar data for an image.
    If the sidecar doesn't exist, returns a minimal default.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        SidecarData object
    """
    sidecar_path = get_sidecar_path(image_path)
    
    if sidecar_path.exists():
        try:
            with open(sidecar_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SidecarData.from_dict(image_path, data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load sidecar {sidecar_path}: {e}")
    
    # Return minimal default
    return SidecarData(image_path=image_path)


def save_sidecar(sidecar: SidecarData, create_backup: bool = True):
    """
    Save sidecar data to disk.
    
    Args:
        sidecar: SidecarData to save
        create_backup: If True, create .bak backup before saving
    """
    sidecar_path = get_sidecar_path(sidecar.image_path)
    
    # Create backup if file exists
    if create_backup and sidecar_path.exists():
        backup_path = Path(str(sidecar_path) + '.bak')
        try:
            backup_path.write_bytes(sidecar_path.read_bytes())
        except IOError as e:
            print(f"Warning: Could not create backup {backup_path}: {e}")
    
    # Save the sidecar
    try:
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(sidecar.to_dict(), f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error: Could not save sidecar {sidecar_path}: {e}")
        raise


def scan_images(root_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Scan a directory for image files.
    
    Args:
        root_path: Root directory to scan
        extensions: List of file extensions to include (default: common image formats)
        
    Returns:
        List of absolute image file paths
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    extensions = [ext.lower() for ext in extensions]
    root = Path(root_path)
    
    if not root.exists() or not root.is_dir():
        return []
    
    images = []
    for file_path in root.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            # Skip .prompt.json files
            if '.prompt.json' not in file_path.name:
                images.append(str(file_path.absolute()))
    
    return sorted(images)


def assemble_prompt(sidecar: SidecarData) -> str:
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
        tags_str = ', '.join(sidecar.tags)
        parts.append(f"Tags: {tags_str}")
    
    return '\n\n'.join(parts)
