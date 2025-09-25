from __future__ import annotations

import warnings
from pathlib import Path
from typing import TypedDict

import yaml

from episcope.library.io.v1_2.timestep import Timestep


class ExperimentMeta(TypedDict):
    sample: str
    replicate: str
    desc: str


class Experiment:
    def __init__(self, directory_path: str | Path) -> None:
        """Initializes the Experiment with a directory path.

        Args:
            directory_path (str): The path to the directory containing the models.

        Raises:
            ValueError: If the provided path is not a directory.
        """
        self.directory_path: Path = Path(directory_path)
        if not self.directory_path.is_dir():
            msg = f"The provided path '{directory_path}' is not a directory."
            raise ValueError(msg)

        self._meta = self._read_meta()
        self._timesteps = {
            path.name: Timestep(path) for path in self._discover_timesteps()
        }

    def _read_meta(self) -> ExperimentMeta | dict:
        """Reads and returns the content of 'meta.yaml' in the directory.

        Returns:
            ExperimentMeta: The content of 'meta.yaml' as a dictionary.
        """
        meta_yaml_path = self.directory_path / "meta.yaml"
        if not meta_yaml_path.exists():
            msg = "No 'meta.yaml' file found in the directory."
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            return {}

        with meta_yaml_path.open("r") as file:
            return yaml.safe_load(file)

    def _discover_timesteps(self):
        for path in self.directory_path.iterdir():
            if path.is_dir():
                yield path
