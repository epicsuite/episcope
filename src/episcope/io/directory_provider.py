from typing import TypedDict, Iterable

import os

class TimeStep(TypedDict):
    """A dictionary representing a time step with a time and a label.

    Attributes:
        name (str): The name of the time step.
        label (str): The label associated with the time step.
    """
    name: str
    label: str

class Dataset(TypedDict):
    """A dictionary representing a dataset with a name and a label.

    Attributes:
        name (str): The name of the dataset.
        label (str): The label associated with the dataset.
    """
    name: str
    label: str

class DirectoryProvider:
    """A class to provide data from a specified directory.

    Attributes:
        directory_path (str): The path to the directory containing the data.
        _timesteps (list[TimeStep]): A list of time steps.
        _variables (list[Variable]): A list of variables.
    """

    def __init__(self, directory_path: str) -> None:
        """Initializes the DataProvider with a directory path.

        Args:
            directory_path (str): The path to the directory containing the data.
        """
        self._directory_path = directory_path
        self._datasets: list[Dataset] = []
        self._timesteps: list[TimeStep] = []
        self._csv_files: dict[tuple[str, str], str] = {}

        self._scan_directory()

    @property
    def datasets(self) -> list[Dataset]:
        """Returns the list of datasets.

        Returns:
            list[Dataset]: A list of datasets.
        """
        return self._datasets

    @property
    def timesteps(self) -> list[TimeStep]:
        """Returns the list of time steps.

        Returns:
            list[TimeStep]: A list of time steps.
        """
        return self._timesteps

    def get_data_file(self, dataset_name: str, timestep_name: str) -> str:
        """Returns the path to a CSV file for the given dataset and timestep.

        Args:
            dataset_name (str): The name of the dataset.
            timestep_name (str): The name of the timestep.

        Returns:
            str: The path to the CSV file.

        Raises:
            ValueError: If a file for the given dataset and timestep cannot be found.
        """
        file_name = f"{dataset_name}_{timestep_name}.csv"
        file_path = os.path.join(self._directory_path, file_name)

        file_path = self._csv_files.get((dataset_name, timestep_name), None)

        if file_path is None:
            raise ValueError(f"File not found for dataset '{dataset_name}' and timestep '{timestep_name}'")

        return file_path

    def _discover_files(self, extensions: Iterable[str]):
        """
        list all the csv files in the given directory.
        """
        extensions_set = set(extensions)

        for name in os.listdir(self._directory_path):
            path = os.path.join(self._directory_path, name)
            if os.path.isfile(path):
                _, ext = os.path.splitext(path)
                if ext in extensions_set:
                    yield path

    def _file_to_dataset_timestamp(self, file_path) -> tuple[str, str]:
        _, file_name = os.path.split(file_path)
        file_name, _ = os.path.splitext(file_name)
        split = file_name.split("_")

        assert len(split) == 2

        timestep, dataset = split

        return dataset, timestep

    def _scan_directory(self):
        csv_files = list(self._discover_files(['.csv']))

        unique_datasets = set()
        unique_timestamps = set()
        self._csv_files = {}

        for csv_file in csv_files:
            (dataset, timestamp) = self._file_to_dataset_timestamp(csv_file)
            unique_datasets.add(dataset)
            unique_timestamps.add(timestamp)
            self._csv_files[(dataset, timestamp)] = csv_file

        self._datasets = list(
            {"name": name, "label": name} for name in unique_datasets
        )
        self._timesteps = list((
            {"name": name, "label": name} for name in unique_timestamps
        ))
