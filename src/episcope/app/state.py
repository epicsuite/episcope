from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from trame_server.state import State


class Representation(TypedDict):
    name: str
    parameters: dict[str, Any]


class Display(TypedDict):
    id: int
    name: str
    type: str
    representation: Representation


class DisplayOption(TypedDict):
    name: str
    type: str
    representations: list[str]


class Quadrant2D(TypedDict):
    pass


class Quadrant3D(TypedDict):
    chromosome: str
    experiment: str
    timestep: str
    displays: dict[str, Display]


@dataclass
class EpiscopeStateAnnotation:
    quadrants_3d: dict[str, Quadrant3D]
    quadrants_2d: dict[str, Quadrant3D]


class StateAdapterQuadrant3D:
    def __init__(self, state: State, quadrant_id: str):
        self.state = state
        self.quadrant_id = quadrant_id

    @property
    def chromosome_key(self):
        return f"quadrant3d_{self.quadrant_id}_chromosome"

    @property
    def chromosome(self):
        return self.state[self.chromosome_key]

    @chromosome.setter
    def chromosome(self, value):
        self.state[self.chromosome_key] = value

    @property
    def experiment_key(self):
        return f"quadrant3d_{self.quadrant_id}_experiment"

    @property
    def experiment(self):
        return self.state[self.experiment_key]

    @experiment.setter
    def experiment(self, value):
        self.state[self.experiment_key] = value

    @property
    def timestep_key(self):
        return f"quadrant3d_{self.quadrant_id}_timestep"

    @property
    def timestep(self):
        return self.state[self.timestep_key]

    @timestep.setter
    def timestep(self, value):
        self.state[self.timestep_key] = value

    @property
    def show_options_key(self):
        return f"quadrant3d_{self.quadrant_id}_show_options"

    @property
    def show_options(self):
        return self.state[self.show_options_key]

    @show_options.setter
    def show_options(self, value):
        self.state[self.show_options_key] = value

    @property
    def has_viz_key(self):
        return f"quadrant3d_{self.quadrant_id}_has_viz"

    @property
    def has_viz(self):
        return self.state[self.has_viz_key]

    @has_viz.setter
    def has_viz(self, value):
        self.state[self.has_viz_key] = value

    @property
    def displays_key(self):
        return f"quadrant3d_{self.quadrant_id}_displays"

    @property
    def displays(self) -> dict[int, Display]:
        return self.state.setdefault(self.displays_key, {})

    @displays.setter
    def displays(self, value: dict[int, Display]):
        self.state[self.displays_key] = value

    @property
    def display_options_key(self):
        return f"quadrant3d_{self.quadrant_id}_display_options_key"

    @property
    def display_options(self) -> dict[str, DisplayOption]:
        return self.state.setdefault(self.display_options_key, {})

    @display_options.setter
    def display_options(self, value: dict[str, DisplayOption]):
        self.state[self.display_options_key] = value


class EpiscopeState(State, EpiscopeStateAnnotation):
    def __init__(self):
        msg = "EpiscopeState is only used as a type hint helper, is not meant to be instantiated."
        raise RuntimeError(msg)
