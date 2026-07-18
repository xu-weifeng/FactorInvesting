from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """
    Load the project's YAML configuration file.

    Parameters
    ----------
    config_path : Path
        Path to the YAML configuration file.

    Returns
    -------
    dict[str, Any]
        Configuration values loaded from the YAML file.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If the YAML file is empty or invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            f"Configuration file is empty or invalid: {config_path}"
        )

    return config


if __name__ == "__main__":
    settings = load_config()
    print(settings)