from __future__ import annotations

import csv
from pathlib import Path
from typing import TypedDict

import yaml

from episcope.library.io import PeakTrackPoint, PointTrackPoint, StructurePoint


class _TimestepMetaTracks(TypedDict):
    peak: dict[str, str]
    point: dict[str, str]


class TimestepMeta(TypedDict):
    tracks: _TimestepMetaTracks
    structure: str


class StructureColumns:
    N_COLUMNS = 5
    CHROMOSOME = 0
    ID = 1
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


class Timestep:
    def __init__(self, directory_path: str | Path) -> None:
        """Initializes the Experiment with a directory path.

        Args:
            directory_path (str): The path to the directory containing the models.

        Raises:
            ValueError: If the provided path is not a directory.
            FileNotFoundError: If 'meta.yaml' is not found in the directory or if no file ending in '*_autosomes.tsv' is found.
        """
        self.directory_path: Path = Path(directory_path)
        if not self.directory_path.is_dir():
            msg = f"The provided path '{directory_path}' is not a directory."
            raise ValueError(msg)

        self._meta = self._read_meta()
        self._structures: dict[str, list[StructurePoint]] = self._read_structure(
            self._meta["structure"]
        )
        self._peak_tracks: dict[str, dict[str, list[PeakTrackPoint]]] = {}
        self._point_tracks: dict[str, dict[str, list[PointTrackPoint]]] = {}

        for track_name, track_path in self._meta["tracks"]["peak"].items():
            self._peak_tracks[track_name] = self._read_peak_track(track_path)

        for track_name, track_path in self._meta["tracks"]["point"].items():
            self._point_tracks[track_name] = self._read_point_track(track_path)

    def _read_meta(self) -> TimestepMeta:
        """Reads and returns the content of 'meta.yaml' in the directory.

        Returns:
            TimestepMeta: The content of 'meta.yaml' as a dictionary.

        Raises:
            FileNotFoundError: If 'meta.yaml' is not found in the directory.
        """
        meta_yaml_path = self.directory_path / "meta.yaml"
        if not meta_yaml_path.exists():
            msg = "No 'meta.yaml' file found in the directory."
            raise FileNotFoundError(msg)

        with meta_yaml_path.open("r") as file:
            return yaml.safe_load(file)

    def _read_structure(self, path: Path):
        structure_path = self.directory_path / path
        if not structure_path.exists():
            msg = f"No structure file found in the directory: {path}"
            raise FileNotFoundError(msg)

        chromosome_structures: dict[str, list[StructurePoint]] = {}

        with structure_path.open("r") as file:
            structure_reader = csv.reader(file)

            # skip header line
            structure_reader.__next__()

            for line in structure_reader:
                assert len(line) == StructureColumns.N_COLUMNS

                chromosome = line[StructureColumns.CHROMOSOME]
                index = int(float(line[StructureColumns.ID])) * 100_000
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

    def _read_peak_track(self, path: Path):
        track_path = self.directory_path / path
        if not track_path.exists():
            msg = f"No peak file found in the directory: {path}"
            raise FileNotFoundError(msg)

        chromosome_track: dict[str, list[PeakTrackPoint]] = {}

        with track_path.open("r") as file:
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
        track_path = self.directory_path / path
        if not track_path.exists():
            msg = f"No point file found in the directory: {path}"
            raise FileNotFoundError(msg)

        chromosome_track: dict[str, list[PointTrackPoint]] = {}

        with track_path.open("r") as file:
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
