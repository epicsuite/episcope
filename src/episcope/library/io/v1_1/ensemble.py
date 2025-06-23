from typing import TypedDict

from pathlib import Path
from typing import Set, Dict, Any
import yaml

from episcope.library.io.v1_1.experiment import Experiment


_ExperimentsMetaStructure = TypedDict("_ExperimentsMetaStructure", {"chromosomes": list[str]})
ExperimentsMeta = TypedDict("ExperimentsMeta", {"structure": _ExperimentsMetaStructure})


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
            FileNotFoundError: If 'meta.yaml' is not found in the directory or if no file ending in '*_autosomes.tsv' is found.
        """
        self.directory_path: Path = Path(directory_path)
        if not self.directory_path.is_dir():
            raise ValueError(f"The provided path '{directory_path}' is not a directory.")
        
        self._chromosomes: Set[str] = self._read_chromosomes()
        self._meta: Dict[str, Any] = self._read_meta()
        self._experiments_meta: ExperimentsMeta = self._read_experiments_meta()
        self._experiments = {
            path.name: Experiment(path) for path in self._discover_experiments()
        }


    def _read_chromosomes(self) -> Set[str]:
        """Finds the first file ending in '*_autosomes.tsv' and reads chromosome names.

        Returns:
            Set[str]: A set of chromosome names.

        Raises:
            FileNotFoundError: If no file ending in '*_autosomes.tsv' is found.
        """
        for file_path in self.directory_path.glob('*_autosomes.tsv'):
            with file_path.open('r') as file:
                chromosome_names = {line.split()[0] for line in file}
            return chromosome_names
        
        raise FileNotFoundError("No file ending in '*_autosomes.tsv' found in the directory.")

    def _read_meta(self) -> Dict[str, Any]:
        """Reads and returns the content of 'meta.yaml' in the directory.

        Returns:
            Dict[str, Any]: The content of 'meta.yaml' as a dictionary.

        Raises:
            FileNotFoundError: If 'meta.yaml' is not found in the directory.
        """
        meta_yaml_path = self.directory_path / 'meta.yaml'
        if not meta_yaml_path.exists():
            raise FileNotFoundError("No 'meta.yaml' file found in the directory.")
        
        with meta_yaml_path.open('r') as file:
            meta_content = yaml.safe_load(file)
        
        return meta_content

    def _read_experiments_meta(self) -> ExperimentsMeta:
        """Reads and returns the content of 'experiments/meta.yaml' in the directory.

        Returns:
            ExperimentsMeta: The content of 'meta.yaml' as a dictionary.

        Raises:
            FileNotFoundError: If 'meta.yaml' is not found in the directory.
        """
        meta_yaml_path = self.directory_path / 'experiments' / 'meta.yaml'
        if not meta_yaml_path.exists():
            raise FileNotFoundError("No 'experiments/meta.yaml' file found in the directory.")
        
        with meta_yaml_path.open('r') as file:
            meta_content = yaml.safe_load(file)
        
        return meta_content

    def _discover_experiments(self):
        experiments_dir = self.directory_path / 'experiments'
        for path in experiments_dir.iterdir():
            if path.is_dir():
                experiment_dir = self.directory_path / path
                yield experiment_dir
