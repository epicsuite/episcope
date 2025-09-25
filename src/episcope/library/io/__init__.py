from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class StructurePoint(TypedDict):
    """A typed dictionary representing a point in 3D space on a chromosome.

    Attributes:
        index: The base pair index of the point along the chromosome.
        position: The 3D coordinates (x, y, z) of the point.
    """

    index: int
    position: tuple[float, float, float]


class PeakTrackPoint(TypedDict):
    """A typed dictionary representing a peak track point.

    Attributes:
        start: The start base pair position of the peak.
        end: The end base pair position of the peak.
        summit: The base pair position at the peak.
        value: The scalar value at the peak.
    """

    start: int
    end: int
    summit: int
    value: float


class PointTrackPoint(TypedDict):
    """A typed dictionary representing a point track point.

    Attributes:
        start: The start base pair position of the point.
        end: The end base pair position of the point.
        value: The scalar value of the point.
    """

    start: int
    end: int
    value: float


class LabelPoint(TypedDict):
    """A typed dictionary representing a text label point.

    Attributes:
        index: The base pair index of the point along the chromosome.
        text: The text of the label.
    """

    index: int
    text: str


class BaseSourceProvider(ABC):
    """Abstract base class for providing genomic data from various sources.

    This class defines the interface for accessing chromosome, experiment, and
    timestep information along with structure and track data.
    """

    @abstractmethod
    def get_chromosomes(
        self,
        experiment: str | None = None,
        timestep: str | None = None,
    ) -> set[str]:
        """Get the set of chromosomes available for the given experiment and timestep.

        Args:
            experiment: The experiment name to filter by, or None for all experiments.
            timestep: The timestep name to filter by, or None for all timesteps.

        Returns:
            A set of chromosome names that match the specified filters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_experiments(
        self,
        chromosome: str | None = None,
        timestep: str | None = None,
    ) -> set[str]:
        """Get the set of experiments available for the given chromosome and timestep.

        Args:
            chromosome: The chromosome name to filter by, or None for all chromosomes.
            timestep: The timestep name to filter by, or None for all timesteps.

        Returns:
            A set of experiment names that match the specified filters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_timesteps(
        self,
        chromosome: str | None = None,
        experiment: str | None = None,
    ) -> set[str]:
        """Get the set of timesteps available for the given chromosome and experiment.

        Args:
            chromosome: The chromosome name to filter by, or None for all chromosomes.
            experiment: The experiment name to filter by, or None for all experiments.

        Returns:
            A set of timestep names that match the specified filters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_peak_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        """Get the set of peak track names for a specific chromosome, experiment, and timestep.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.

        Returns:
            A set of peak track names available for the specified parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_point_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        """Get the set of point track names for a specific chromosome, experiment, and timestep.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.

        Returns:
            A set of point track names available for the specified parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def get_structure(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> list[StructurePoint]:
        """Get the structure data for a specific chromosome, experiment, and timestep.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.

        Returns:
            A list of StructurePoint objects representing the 3D structure of the chromosome.
        """
        raise NotImplementedError

    @abstractmethod
    def get_peak_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ) -> list[PeakTrackPoint]:
        """Get the peak track data for a specific chromosome, experiment, timestep, and track.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.
            track: The track name.

        Returns:
            A list of PeakTrackPoint objects representing the peak data.
        """
        raise NotImplementedError

    @abstractmethod
    def get_point_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ) -> list[PointTrackPoint]:
        """Get the point track data for a specific chromosome, experiment, timestep, and track.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.
            track: The track name.

        Returns:
            A list of PointTrackPoint objects representing the point data.
        """
        raise NotImplementedError

    @abstractmethod
    def get_labels(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> list[LabelPoint]:
        """Get the labels data for a specific chromosome, experiment, and timestep.

        Args:
            chromosome: The chromosome name.
            experiment: The experiment name.
            timestep: The timestep name.

        Returns:
            A list of LabelPoint objects representing the text labels along the chromosome.
        """
        raise NotImplementedError
