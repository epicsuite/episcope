from typing import Optional, TypedDict

from abc import ABC, abstractmethod

class StructurePoint(TypedDict):
    index: int
    position: tuple[float, float, float]


class PeakTrackPoint(TypedDict):
    start: int
    end: int
    summit: int
    value: float


class PointTrackPoint(TypedDict):
    start: int
    end: int
    value: float


class BaseSourceProvider(ABC):
    @abstractmethod
    def get_chromosomes(
        self,
        experiment: Optional[str] = None,
        timestep: Optional[str] = None,
    ) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_experiments(
        self,
        chromosome: Optional[str] = None,
        timestep: Optional[str] = None,
    ) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_timesteps(
        self,
        chromosome: Optional[str] = None,
        experiment: Optional[str] = None,
    ) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_peak_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_point_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_structure(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> list[StructurePoint]:
        raise NotImplementedError

    @abstractmethod
    def get_peak_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ) -> list[PeakTrackPoint]:
        raise NotImplementedError

    @abstractmethod
    def get_point_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ) -> list[PointTrackPoint]:
        raise NotImplementedError
