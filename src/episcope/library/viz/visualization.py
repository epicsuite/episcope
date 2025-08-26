from __future__ import annotations

from typing import Literal, TypedDict

from paraview import simple
from vtkmodules.vtkCommonComputationalGeometry import vtkCardinalSpline

from episcope.library.io import BaseSourceProvider
from episcope.library.viz.common import CardinalSplines
from episcope.library.viz.data_source import (
    PeakTrackSource,
    PointTrackSource,
    StructureSource,
)
from episcope.library.viz.display import (
    DelaunayDisplay,
    LowerGaussianContourDisplay,
    TubeDisplay,
    UpperGaussianContourDisplay,
)

TrackType = Literal["point", "peak"]


class DisplayMeta(TypedDict):
    track_name: str
    track_type: TrackType
    # display: Display
    enabled: bool


class Visualization:
    def __init__(self, source_provider: BaseSourceProvider, render_view):
        self._source = source_provider
        self.render_view = render_view
        self._chromosome = ""
        self._experiment = ""
        self._timestep = ""
        self._splines: CardinalSplines = {
            "x": vtkCardinalSpline(),
            "y": vtkCardinalSpline(),
            "z": vtkCardinalSpline(),
        }
        self._dataset_timestamp: tuple[str, str] = ("", "")
        self._displays: dict[int, DisplayMeta] = {}
        self._display_id = 0

    def set_chromosome(self, chromosome: str, experiment: str, timestep: str):
        self._chromosome = chromosome
        self._experiment = experiment
        self._timestep = timestep

        structure = self._source.get_structure(chromosome, experiment, timestep)

        for coord in ("x", "y", "z"):
            self._splines[coord].RemoveAllPoints()

        for structure_point in structure:
            for i, coord in enumerate(("x", "y", "z")):
                self._splines[coord].AddPoint(
                    structure_point["index"], structure_point["position"][i]
                )

        for coord in ("x", "y", "z"):
            self._splines[coord].Compute()

    def add_structure_display(self, display_type: str, point_spacing: int):
        structure = self._source.get_structure(
            self._chromosome, self._experiment, self._timestep
        )

        structure_indices = [p["index"] for p in structure]

        structure_source = StructureSource()
        structure_source.set_splines(self._splines)
        structure_source.set_data(structure_indices, point_spacing)

        if display_type == "tube":
            display = TubeDisplay()
            display.input = structure_source.output
            display.variable = ""
            repr_props = display.representation_properties
        elif display_type == "delaunay":
            display = DelaunayDisplay()
            display.input = structure_source.output
            repr_props = display.representation_properties
        else:
            display = structure_source
            repr_props = {}

        representation = simple.Show(
            display.output, self.render_view, "GeometryRepresentation"
        )

        for k, v in repr_props.items():
            representation.__setattr__(k, v)

    def add_peak_display(self, track_name: str, display_type: str, point_spacing: int):
        track = self._source.get_peak_track(
            self._chromosome, self._experiment, self._timestep, track_name
        )

        track_source = PeakTrackSource()
        track_source.set_splines(self._splines)
        track_source.set_data(track, point_spacing)

        if display_type == "tube":
            display = TubeDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "lower_gaussian_contour":
            display = LowerGaussianContourDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "upper_gaussian_contour":
            display = UpperGaussianContourDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "delaunay":
            display = DelaunayDisplay()
            display.input = track_source.output
            repr_props = display.representation_properties
        else:
            display = track_source
            repr_props = {}

        representation = simple.Show(display.output, self.render_view)

        for k, v in repr_props.items():
            representation.__setattr__(k, v)

    def add_point_display(self, track_name: str, display_type: str, point_spacing: int):
        track = self._source.get_point_track(
            self._chromosome, self._experiment, self._timestep, track_name
        )

        track_source = PointTrackSource()
        track_source.set_splines(self._splines)
        track_source.set_data(track, point_spacing)

        if display_type == "tube":
            display = TubeDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "lower_gaussian_contour":
            display = LowerGaussianContourDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "upper_gaussian_contour":
            display = UpperGaussianContourDisplay()
            display.input = track_source.output
            display.variable = "scalars"
            repr_props = display.representation_properties
        elif display_type == "delaunay":
            display = DelaunayDisplay()
            display.input = track_source.output
            repr_props = display.representation_properties
        else:
            display = track_source
            repr_props = {}

        representation = simple.Show(display.output, self.render_view)

        for k, v in repr_props.items():
            representation.__setattr__(k, v)

    def modify_display(self, display_id: int, variable: str, display_type: str):
        raise NotImplementedError

    def remove_display(self, display_id: int):
        raise NotImplementedError

    def _update_displays(self):
        for _display_id, display_meta in self._displays.items():
            _track_name = display_meta["track_name"]
            track_type = display_meta["track_type"]
            _enabled = display_meta["enabled"]

            track_data = None
            try:
                if track_type == "peak":
                    track_data = self._source.get_peak_track(
                        self._chromosome, self._experiment, self._timestep
                    )
                else:
                    track_data = self._source.get_point_track(
                        self._chromosome, self._experiment, self._timestep
                    )

            except KeyError:
                pass

            if track_data is None:
                display_meta["enabled"] = False
            else:
                display_meta["enabled"] = True
