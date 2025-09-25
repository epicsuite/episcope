from __future__ import annotations

import csv
from pathlib import Path
from typing import TypedDict

from episcope.library.io import (
    LabelPoint,
    PeakTrackPoint,
    PointTrackPoint,
    StructurePoint,
)


class _TimestepMetaTracks(TypedDict):
    peak: dict[str, str]
    point: dict[str, str]


class TimestepMeta(TypedDict):
    tracks: _TimestepMetaTracks
    structure: str


class StructureColumns:
    N_COLUMNS = 5
    CHROMOSOME = 0
    INDEX = 1
    X = 2
    Y = 3
    Z = 4


class PeakTrackColumns:
    N_COLUMNS = 10
    CHROMOSOME = 0
    START = 1
    END = 2
    VALUE = 4
    SUMMIT = 9


class PointTrackColumns:
    N_COLUMNS = 4
    CHROMOSOME = 0
    START = 1
    END = 2
    VALUE = 3


class LabelsColumns:
    N_COLUMNS = 3
    CHROMOSOME = 0
    INDEX = 1
    TEXT = 2


class Timestep:
    def __init__(self, directory_path: str | Path) -> None:
        """Initializes the Experiment with a directory path.

        Args:
            directory_path (str): The path to the directory containing the models.

        Raises:
            ValueError: If the provided path is not a directory.
            FileNotFoundError: If 'structure.csv' is not found in the directory.
        """
        self.directory_path: Path = Path(directory_path)
        if not self.directory_path.is_dir():
            msg = f"The provided path '{directory_path}' is not a directory."
            raise ValueError(msg)

        structure_file = self.directory_path / "structure.csv"
        if not structure_file.exists():
            msg = "No structure file (structure.csv) found in the directory."
            raise FileNotFoundError(msg)

        self._structures = self._read_structure(structure_file)

        labels_file = self.directory_path / "labels.csv"
        if not labels_file.exists():
            self._labels = {}
        else:
            self._labels = self._read_labels(labels_file)

        self._peak_tracks = {
            track_stem: self._read_peak_track(track_path)
            for track_path, track_stem in self._discover_files("narrowPeak")
        }

        self._point_tracks = {
            track_stem: self._read_point_track(track_path)
            for track_path, track_stem in self._discover_files("bed")
        }

    def _discover_files(self, extension: str):
        """Discover files with a specific extension in the timestep directory.

        Args:
            extension (str): The file extension to look for (e.g., 'narrowPeak').

        Yields:
            tuple[Path, str]: A tuple containing the full path of the file and its base name.
        """
        for file_path in self.directory_path.glob(f"*.{extension}"):
            if file_path.is_file():
                yield (file_path, file_path.stem)

    def _read_structure(self, path: Path):
        chromosome_structures: dict[str, list[StructurePoint]] = {}

        with path.open("r") as file:
            structure_reader = csv.reader(file)

            # skip header line
            structure_reader.__next__()

            for line in structure_reader:
                assert len(line) == StructureColumns.N_COLUMNS

                chromosome = line[StructureColumns.CHROMOSOME]
                index = int(float(line[StructureColumns.INDEX]))
                x = float(line[StructureColumns.X])
                y = float(line[StructureColumns.Y])
                z = float(line[StructureColumns.Z])

                structure = chromosome_structures.setdefault(chromosome, [])

                structure.append(
                    {
                        "index": index,
                        "position": (x, y, z),
                    }
                )

        return chromosome_structures

    def _read_labels(self, path: Path):
        chromosome_labels: dict[str, list[LabelPoint]] = {}

        with path.open("r") as file:
            labels_reader = csv.reader(file)

            # skip header line
            # structure_reader.__next__()

            for line in labels_reader:
                assert len(line) == LabelsColumns.N_COLUMNS

                chromosome = line[LabelsColumns.CHROMOSOME]
                index = int(float(line[LabelsColumns.INDEX]))
                text = line[LabelsColumns.TEXT]

                labels = chromosome_labels.setdefault(chromosome, [])

                labels.append(
                    {
                        "index": index,
                        "text": text,
                    }
                )

        return chromosome_labels

    def _read_peak_track(self, path: Path):
        chromosome_track: dict[str, list[PeakTrackPoint]] = {}

        with path.open("r") as file:
            track_reader = csv.reader(file, delimiter="\t")

            for line in track_reader:
                assert len(line) == PeakTrackColumns.N_COLUMNS

                chromosome = line[PeakTrackColumns.CHROMOSOME]
                start = int(float(line[PeakTrackColumns.START]))
                end = int(float(line[PeakTrackColumns.END]))
                value = float(line[PeakTrackColumns.VALUE])
                summit = start + int(float(line[PeakTrackColumns.SUMMIT]))

                track = chromosome_track.setdefault(chromosome, [])

                track.append(
                    {
                        "start": start,
                        "end": end,
                        "summit": summit,
                        "value": value,
                    }
                )

        return chromosome_track

    def _read_point_track(self, path: Path):
        chromosome_track: dict[str, list[PointTrackPoint]] = {}

        with path.open("r") as file:
            track_reader = csv.reader(file, delimiter="\t")

            for line in track_reader:
                assert len(line) == PointTrackColumns.N_COLUMNS

                chromosome = line[PointTrackColumns.CHROMOSOME]
                start = int(float(line[PointTrackColumns.START]))
                end = int(float(line[PointTrackColumns.END]))
                try:
                    value = float(line[PointTrackColumns.VALUE])
                except ValueError:
                    continue

                track = chromosome_track.setdefault(chromosome, [])

                track.append(
                    {
                        "start": start,
                        "end": end,
                        "value": value,
                    }
                )

        return chromosome_track
