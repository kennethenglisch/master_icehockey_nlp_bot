__version__ = "0.0.1"

from pathlib import Path

_package_dir = Path(__file__).resolve().parent
app_dir = _package_dir.parent.parent
config_dir = app_dir / "config"
data_dir = app_dir / "data"
