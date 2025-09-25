from __future__ import annotations

from episcope.library.io import BaseSourceProvider
from episcope.library.io.v1_2.ensemble import Ensemble


class SourceProvider(BaseSourceProvider):
    def __init__(self, ensemble: Ensemble):
        self._ensemble = ensemble

    def get_chromosomes(
        self,
        experiment: str | None = None,
        timestep: str | None = None,
    ) -> set[str]:
        chromosomes = set()

        for _experiment_name, _experiment in self._ensemble._experiments.items():
            if experiment is not None and _experiment_name != experiment:
                continue

            for _timestep_name, _timestep in _experiment._timesteps.items():
                if timestep is not None and _timestep_name != timestep:
                    continue

                for _chromosome in _timestep._structures:
                    chromosomes.add(_chromosome)

        return chromosomes

    def get_experiments(
        self,
        chromosome: str | None = None,
        timestep: str | None = None,
    ) -> set[str]:
        experiments = set()

        for _experiment_name, _experiment in self._ensemble._experiments.items():
            add_experiment = False

            for _timestep_name, _timestep in _experiment._timesteps.items():
                if timestep is not None and _timestep_name != timestep:
                    continue

                for _chromosome_name in _timestep._structures:
                    if chromosome is not None and _chromosome_name != chromosome:
                        continue

                    add_experiment = True

            if add_experiment:
                experiments.add(_experiment_name)

        return experiments

    def get_timesteps(
        self,
        chromosome: str | None = None,
        experiment: str | None = None,
    ) -> set[str]:
        experiments = set()

        for _experiment_name, _experiment in self._ensemble._experiments.items():
            if experiment is not None and _experiment_name != experiment:
                continue

            for _timestep_name, _timestep in _experiment._timesteps.items():
                add_timestep = False

                for _chromosome_name in _timestep._structures:
                    if chromosome is not None and _chromosome_name != chromosome:
                        continue

                    add_timestep = True

                if add_timestep:
                    experiments.add(_timestep_name)

        return experiments

    def get_peak_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]

        tracks = set()
        for _track_name, _track in _timestep._peak_tracks.items():
            if chromosome in _track:
                tracks.add(_track_name)

        return tracks

    def get_point_tracks(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ) -> set[str]:
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]

        tracks = set()
        for _track_name, _track in _timestep._point_tracks.items():
            if chromosome in _track:
                tracks.add(_track_name)

        return tracks

    def get_structure(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ):
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]

        return _timestep._structures[chromosome]

    def get_peak_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ):
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]
        _track = _timestep._peak_tracks[track]

        return _track[chromosome]

    def get_point_track(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
        track: str,
    ):
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]
        _track = _timestep._point_tracks[track]

        return _track[chromosome]

    def get_labels(
        self,
        chromosome: str,
        experiment: str,
        timestep: str,
    ):
        _experiment = self._ensemble._experiments[experiment]
        _timestep = _experiment._timesteps[timestep]

        return _timestep._labels.get(chromosome, [])
