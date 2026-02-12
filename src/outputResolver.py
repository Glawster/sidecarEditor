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
    
    def __init__(self, output_root: Optional[str] = None):
        """
        Initialize the output resolver.
        
        Args:
            output_root: Root directory where output images are stored
        """
        self.output_root = Path(output_root) if output_root else None
    
    def set_output_root(self, output_root: str):
        """
        Set or update the output root directory.
        
        Args:
            output_root: Root directory where output images are stored
        """
        self.output_root = Path(output_root) if output_root else None
    
    def resolve_output(self, original_path: str, input_root: Optional[str] = None) -> Optional[str]:
        """
        Attempt to find the output image for an original image.
        
        Resolution strategy:
        1. Try same relative path from input_root to output_root
        2. Try filename match in output_root
        3. Try stem-prefix match (e.g., "image" matches "image_001.png")
        
        Args:
            original_path: Path to the original image
            input_root: Root directory of input images (for relative path calculation)
            
        Returns:
            Path to output image if found, None otherwise
        """
        if not self.output_root or not self.output_root.exists():
            return None
        
        original = Path(original_path)
        
        # Strategy 1: Same relative path
        if input_root:
            try:
                rel_path = original.relative_to(input_root)
                output_path = self.output_root / rel_path
                if output_path.exists():
                    return str(output_path)
            except (ValueError, OSError):
                pass
        
        # Strategy 2: Filename match
        filename_match = self._find_by_filename(original.name)
        if filename_match:
            return filename_match
        
        # Strategy 3: Stem-prefix match
        stem_match = self._find_by_stem_prefix(original.stem)
        if stem_match:
            return stem_match
        
        return None
    
    def _find_by_filename(self, filename: str) -> Optional[str]:
        """
        Find a file with exact filename match in output_root.
        
        Args:
            filename: Filename to search for
            
        Returns:
            Path to matching file if found, None otherwise
        """
        if not self.output_root:
            return None
        
        for file_path in self.output_root.rglob(filename):
            if file_path.is_file():
                return str(file_path)
        
        return None
    
    def _find_by_stem_prefix(self, stem: str) -> Optional[str]:
        """
        Find a file whose stem starts with the given stem.
        E.g., "image" matches "image_001.png", "image_final.jpg"
        
        Args:
            stem: Filename stem to match as prefix
            
        Returns:
            Path to first matching file if found, None otherwise
        """
        if not self.output_root:
            return None
        
        # Common image extensions to check
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        for file_path in self.output_root.rglob('*'):
            if file_path.is_file():
                if file_path.stem.startswith(stem) and file_path.suffix.lower() in extensions:
                    return str(file_path)
        
        return None
    
    def get_possible_outputs(self, original_path: str, input_root: Optional[str] = None) -> List[str]:
        """
        Get all possible output images for an original image.
        Useful for debugging or presenting multiple options to the user.
        
        Args:
            original_path: Path to the original image
            input_root: Root directory of input images
            
        Returns:
            List of possible output image paths
        """
        if not self.output_root or not self.output_root.exists():
            return []
        
        original = Path(original_path)
        results = []
        
        # Collect all candidates
        candidates = set()
        
        # From relative path
        if input_root:
            try:
                rel_path = original.relative_to(input_root)
                output_path = self.output_root / rel_path
                if output_path.exists():
                    candidates.add(str(output_path))
            except (ValueError, OSError):
                pass
        
        # From filename matches
        for file_path in self.output_root.rglob(original.name):
            if file_path.is_file():
                candidates.add(str(file_path))
        
        # From stem-prefix matches
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        for file_path in self.output_root.rglob('*'):
            if file_path.is_file():
                if file_path.stem.startswith(original.stem) and file_path.suffix.lower() in extensions:
                    candidates.add(str(file_path))
        
        return sorted(list(candidates))
