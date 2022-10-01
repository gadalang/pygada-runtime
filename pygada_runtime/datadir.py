"""Gada has a special directory for storing global configuration."""
from __future__ import annotations

__all__ = ["path", "load_config", "write_config"]
import os
import sys
import pathlib
import yaml
from typing import Optional


def path() -> str:
    """Get abolute path to the data directory.

    * Windows: ``AppData/Roaming/Gada``
    * Linux: ``.local/share/gada``
    * Mac: ``Library/Application Support/Gada``

    Will raise **NotImplementedError** on unsupported platforms.

    :return: path to data directory
    """
    home = pathlib.Path.home().absolute()

    if sys.platform == "win32":
        return str(home / "AppData" / "Roaming" / "Gada")
    elif sys.platform == "linux":
        return str(home / ".local" / "share" / "gada")
    elif sys.platform == "darwin":
        return str(home / "Library" / "Application Support" / "Gada")

    raise NotImplementedError()


def load_config() -> dict:
    """Load ``{datadir}/config.yml``.

    An empty configuration will be returned if an error occurs.

    :return: configuration
    """
    try:
        data_dir = path()

        with open(
            os.path.join(data_dir, "config.yml"), "r", encoding="utf-8"
        ) as f:
            return yaml.safe_load(f.read())
    except Exception:
        return {}


def write_config(config: Optional[dict] = None) -> None:
    """Override ``{datadir}/config.yml``.

    :param config: new configuration
    """
    data_dir = path()
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "config.yml"), "w", encoding="utf-8") as f:
        f.write(yaml.safe_dump(config))
