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
sidecarEditorKey = "sidecarEditor"

# In-memory config cache (will be replaced with actual kohyaConfig when integrated)
_configCache: Dict[str, Any] = {}


def _loadConfig() -> Dict[str, Any]:
    """Load configuration (placeholder until kohyaConfig is integrated)."""
    # TODO: Replace with kohyaConfig.loadConfig()
    import json
    from pathlib import Path

    configPath = Path.home() / ".config" / "kohya" / "kohyaConfig.json"

    if configPath.exists():
        try:
            with open(configPath, "r") as f:
                return json.load(f)
        except:
            pass

    return {}


def _saveConfig(config: Dict[str, Any]):
    """Save configuration (placeholder until kohyaConfig is integrated)."""
    # TODO: Replace with kohyaConfig.saveConfig(config)
    import json
    from pathlib import Path

    configPath = Path.home() / ".config" / "kohya" / "kohyaConfig.json"
    configPath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(configPath, "w") as f:
            json.dump(config, f, indent=2)
    except:
        pass


def _getSidecarSection() -> Dict[str, Any]:
    """Get the sidecarEditor section from config."""
    config = _loadConfig()
    return config.get(sidecarEditorKey, {})


def _saveSidecarSection(section: Dict[str, Any]):
    """Save the sidecarEditor section to config."""
    config = _loadConfig()
    config[sidecarEditorKey] = section
    _saveConfig(config)

def getInputRoot() -> Optional[str]:
    config = _loadConfig()

    # 1️⃣ Preferred: sidecarEditor section
    sidecar = config.get("sidecarEditor", {})
    inputRoot = sidecar.get("inputRoot")
    if inputRoot:
        return inputRoot

    # 2️⃣ Fallback: global comfyInput
    inputRoot = config.get("comfyInput")
    if inputRoot:
        return inputRoot

    return None


def getOutputRoot() -> Optional[str]:
    config = _loadConfig()

    # 1️⃣ Preferred: sidecarEditor section
    sidecar = config.get("sidecarEditor", {})
    outputRoot = sidecar.get("outputRoot")
    if outputRoot:
        return outputRoot

    # 2️⃣ Fallback: global comfyOutput
    outputRoot = config.get("comfyOutput")
    if outputRoot:
        return outputRoot

    return None

def setInputRoot(path: str):
    """
    Set the input root directory.

    Args:
        path: Input root directory path
    """
    section = _getSidecarSection()
    section["inputRoot"] = path
    _saveSidecarSection(section)


def setOutputRoot(path: str):
    """
    Set the output root directory.

    Args:
        path: Output root directory path
    """
    section = _getSidecarSection()
    section["outputRoot"] = path
    _saveSidecarSection(section)


def getWindowGeometry() -> Optional[dict]:
    """
    Get the saved window geometry.

    Returns:
        Dictionary with window geometry (x, y, width, height) or None
    """
    section = _getSidecarSection()
    return section.get("windowGeometry")


def setWindowGeometry(x: int, y: int, width: int, height: int):
    """
    Save the window geometry.

    Args:
        x: Window x position
        y: Window y position
        width: Window width
        height: Window height
    """
    section = _getSidecarSection()
    section["windowGeometry"] = {"x": x, "y": y, "width": width, "height": height}
    _saveSidecarSection(section)


def getLastSelectedImage() -> Optional[str]:
    """
    Get the last selected image path.

    Returns:
        Image path or None if not set
    """
    section = _getSidecarSection()
    return section.get("lastSelectedImage")


def setLastSelectedImage(path: str):
    """
    Set the last selected image path.

    Args:
        path: Image file path
    """
    section = _getSidecarSection()
    section["lastSelectedImage"] = path
    _saveSidecarSection(section)


def getRunpodPodId() -> Optional[str]:
    """
    Get the RunPod Pod ID for the remote ComfyUI server.
    This is the primary/preferred way to connect to ComfyUI.
    The Pod ID is used to build the proxy URL:
        https://{podId}-8188.proxy.runpod.net

    Returns:
        RunPod Pod ID string or None if not configured
    """
    config = _loadConfig()
    sidecar = config.get("sidecarEditor", {})
    podId = sidecar.get("runpodPodId")
    if podId:
        return podId
    return config.get("runpodPodId") or None


def setRunpodPodId(podId: str):
    """
    Set the RunPod Pod ID for the remote ComfyUI server.

    Args:
        podId: RunPod Pod ID (e.g. abc123xyz)
    """
    section = _getSidecarSection()
    section["runpodPodId"] = podId
    _saveSidecarSection(section)


def getTxt2ImgScriptPath() -> Optional[str]:
    """
    Get the path to the txt2imgComfy.py script from linuxMigration repo.

    Returns:
        Path string or None if not configured
    """
    section = _getSidecarSection()
    return section.get("txt2ImgScriptPath")


def setTxt2ImgScriptPath(path: str):
    """
    Set the path to the txt2imgComfy.py script.

    Args:
        path: Absolute path to txt2imgComfy.py
    """
    section = _getSidecarSection()
    section["txt2ImgScriptPath"] = path
    _saveSidecarSection(section)


def getComfyUrl() -> Optional[str]:
    """
    Get the ComfyUI base URL.  Prefers the sidecarEditor section;
    falls back to the global 'comfyUrl' key.

    Returns:
        URL string or None if not configured
    """
    config = _loadConfig()
    sidecar = config.get("sidecarEditor", {})
    url = sidecar.get("comfyUrl")
    if url:
        return url
    return config.get("comfyUrl") or None


def setComfyUrl(url: str):
    """
    Set the ComfyUI base URL in the sidecarEditor config section.

    Args:
        url: ComfyUI base URL (e.g. http://127.0.0.1:8188)
    """
    section = _getSidecarSection()
    section["comfyUrl"] = url
    _saveSidecarSection(section)


def getAllSettings() -> dict:
    """
    Get all sidecar editor settings.

    Returns:
        Dictionary of all settings
    """
    return _getSidecarSection()


def setAllSettings(settings: dict):
    """
    Set all sidecar editor settings at once.

    Args:
        settings: Dictionary of settings to save
    """
    _saveSidecarSection(settings)
