"""
Configuration management for Sidecar Editor.
Thin wrapper around kohyaConfig.py that provides sidecar-specific settings.

Note: kohyaConfig.py is expected to be available from the linuxMigration repository.
For now, we'll use a minimal implementation until the dependency is properly set up.
"""

from typing import Optional, Dict, Any

# TODO: Import from linuxMigration/kohyaTools/kohyaConfig.py when available
# For now, use a local minimal implementation

# Configuration key for all sidecar editor settings
SIDECAR_EDITOR_KEY = "sidecarEditor"

# In-memory config cache (will be replaced with actual kohyaConfig when integrated)
_config_cache: Dict[str, Any] = {}


def _load_config() -> Dict[str, Any]:
    """Load configuration (placeholder until kohyaConfig is integrated)."""
    # TODO: Replace with kohyaConfig.loadConfig()
    import json
    from pathlib import Path
    
    config_path = Path.home() / ".config" / "kohya" / "kohyaConfig.json"
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {}


def _save_config(config: Dict[str, Any]):
    """Save configuration (placeholder until kohyaConfig is integrated)."""
    # TODO: Replace with kohyaConfig.saveConfig(config)
    import json
    from pathlib import Path
    
    config_path = Path.home() / ".config" / "kohya" / "kohyaConfig.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass


def _get_sidecar_section() -> Dict[str, Any]:
    """Get the sidecarEditor section from config."""
    config = _load_config()
    return config.get(SIDECAR_EDITOR_KEY, {})


def _save_sidecar_section(section: Dict[str, Any]):
    """Save the sidecarEditor section to config."""
    config = _load_config()
    config[SIDECAR_EDITOR_KEY] = section
    _save_config(config)


def get_input_root() -> Optional[str]:
    """
    Get the last-used input root directory.
    
    Returns:
        Input root path or None if not set
    """
    section = _get_sidecar_section()
    return section.get('inputRoot')


def set_input_root(path: str):
    """
    Set the input root directory.
    
    Args:
        path: Input root directory path
    """
    section = _get_sidecar_section()
    section['inputRoot'] = path
    _save_sidecar_section(section)


def get_output_root() -> Optional[str]:
    """
    Get the last-used output root directory.
    
    Returns:
        Output root path or None if not set
    """
    section = _get_sidecar_section()
    return section.get('outputRoot')


def set_output_root(path: str):
    """
    Set the output root directory.
    
    Args:
        path: Output root directory path
    """
    section = _get_sidecar_section()
    section['outputRoot'] = path
    _save_sidecar_section(section)


def get_window_geometry() -> Optional[dict]:
    """
    Get the saved window geometry.
    
    Returns:
        Dictionary with window geometry (x, y, width, height) or None
    """
    section = _get_sidecar_section()
    return section.get('windowGeometry')


def set_window_geometry(x: int, y: int, width: int, height: int):
    """
    Save the window geometry.
    
    Args:
        x: Window x position
        y: Window y position
        width: Window width
        height: Window height
    """
    section = _get_sidecar_section()
    section['windowGeometry'] = {
        'x': x,
        'y': y,
        'width': width,
        'height': height
    }
    _save_sidecar_section(section)


def get_last_selected_image() -> Optional[str]:
    """
    Get the last selected image path.
    
    Returns:
        Image path or None if not set
    """
    section = _get_sidecar_section()
    return section.get('lastSelectedImage')


def set_last_selected_image(path: str):
    """
    Set the last selected image path.
    
    Args:
        path: Image file path
    """
    section = _get_sidecar_section()
    section['lastSelectedImage'] = path
    _save_sidecar_section(section)


def get_all_settings() -> dict:
    """
    Get all sidecar editor settings.
    
    Returns:
        Dictionary of all settings
    """
    return _get_sidecar_section()


def set_all_settings(settings: dict):
    """
    Set all sidecar editor settings at once.
    
    Args:
        settings: Dictionary of settings to save
    """
    _save_sidecar_section(settings)
