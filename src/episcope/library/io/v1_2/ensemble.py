from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, TypedDict

import yaml

from episcope.library.io.v1_2.experiment import Experiment


class _ExperimentsMetaStructure(TypedDict):
    chromosomes: list[str]


class ExperimentsMeta(TypedDict):
    structure: _ExperimentsMetaStructure


class Ensemble:
    """A class to represent an ensemble of models stored in a directory.

    Attributes:
        directory_path (Path): The path to the directory containing the models.
        _chromosomes (Set[str]): A set of chromosome names.
        _meta (Dict[str, Any]): The content of 'meta.yaml' as a dictionary.
    """

    def __init__(self, directory_path: str | Path) -> None:
        """Initializes the Ensemble with a directory path.

        Args:
            directory_path (str): The path to the directory containing the models.

        Raises:
            ValueError: If the provided path is not a directory.
        """
        self.directory_path: Path = Path(directory_path)
        if not self.directory_path.is_dir():
            msg = f"The provided path '{directory_path}' is not a directory."
            raise ValueError(msg)

        self._chromosomes: set[str] = self._read_chromosomes()
        self._meta: dict[str, Any] = self._read_meta()
        self._experiments_meta: ExperimentsMeta = self._read_experiments_meta()
        self._experiments = {
            path.name: Experiment(path) for path in self._discover_experiments()
        }

    def _read_chromosomes(self) -> set[str]:
        """Finds the first file ending in '*_autosomes.tsv' and reads chromosome names.

        Returns:
            Set[str]: A set of chromosome names.
        """
        chromosomes_path = self.directory_path / "provenance" / "contigs.tsv"
        if not chromosomes_path.exists():
            msg = "No 'provenance/contigs.tsv' file found in the directory."
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            return set()

        with chromosomes_path.open("r") as file:
            return {line.split()[0] for line in file}

    def _read_meta(self) -> dict[str, Any]:
        """Reads and returns the content of 'meta.yaml' in the directory.

        Returns:
            Dict[str, Any]: The content of 'meta.yaml' as a dictionary.
        """
        meta_yaml_path = self.directory_path / "meta.yaml"
        if not meta_yaml_path.exists():
            msg = "No 'meta.yaml' file found in the directory."
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            return {}

        with meta_yaml_path.open("r") as file:
            return yaml.safe_load(file)

    def _read_experiments_meta(self) -> ExperimentsMeta:
        """Reads and returns the content of 'experiments/meta.yaml' in the directory.

        Returns:
            ExperimentsMeta: The content of 'meta.yaml' as a dictionary.
        """
        meta_yaml_path = self.directory_path / "experiments" / "meta.yaml"
        if not meta_yaml_path.exists():
            msg = "No 'experiments/meta.yaml' file found in the directory."
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            return {"structure": {"chromosomes": []}}

        with meta_yaml_path.open("r") as file:
            return yaml.safe_load(file)

    def _discover_experiments(self):
        experiments_dir = self.directory_path / "experiments"
        for path in experiments_dir.iterdir():
            if path.is_dir():
                experiment_dir = self.directory_path / path
                yield experiment_dir
