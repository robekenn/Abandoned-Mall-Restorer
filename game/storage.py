"""Platform save locations and atomic writes, independent of game simulation."""

import os
from pathlib import Path
import sys
import tempfile


def save_directory():
    """Use the same per-user directory for source and packaged launches."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "MallRestorer"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MallRestorer"
    return (
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        / "MallRestorer"
    )


def atomic_write(path, content):
    """Flush a temporary sibling before replacing the destination atomically."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
