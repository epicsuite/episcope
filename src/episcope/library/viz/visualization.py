from __future__ import annotations

from typing import Any, Literal, TypedDict

from paraview import simple
from vtkmodules.vtkCommonComputationalGeometry import vtkCardinalSpline

from episcope.library.io import BaseSourceProvider
from episcope.library.viz.alignment import align_structures
from episcope.library.viz.common import CardinalSplines
from episcope.library.viz.data_source import (
    DataSource,
    PeakTrackSource,
    PointTrackSource,
    StructureSource,
)
from episcope.library.viz.display import (
    DelaunayDisplay,
    Display,
    LowerGaussianContourDisplay,
    TubeDisplay,
    UpperGaussianContourDisplay,
)

TrackType = Literal["point", "peak", "structure"]


class DisplayMeta(TypedDict):
    track_name: str
    track_type: TrackType
    display: Display
    source: DataSource
    repr_props: dict
    representation: Any
    enabled: bool


class SourceMeta(TypedDict):
    source_name: str
    source_type: TrackType
    source: DataSource


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
        self._sources: dict[str, SourceMeta] = {}
        self._display_id = 0

    def align(self, other: Visualization | None):
        structure = self._source.get_structure(
            self._chromosome, self._experiment, self._timestep
        )

        if other is None or other is self:
            aligned_structure = structure
        else:
            structure_other = other._source.get_structure(
                other._chromosome, other._experiment, other._timestep
            )
            aligned_structure = align_structures(structure, structure_other, 100)

        for coord in ("x", "y", "z"):
            self._splines[coord].RemoveAllPoints()

        for structure_point in aligned_structure:
            for i, coord in enumerate(("x", "y", "z")):
                self._splines[coord].AddPoint(
                    structure_point["index"], structure_point["position"][i]
                )

        for coord in ("x", "y", "z"):
            self._splines[coord].Compute()

        for source_meta in self._sources.values():
            source_meta["source"].update()

        for display_meta in self._displays.values():
            simple.Delete(display_meta["display"].output)
            representation = simple.Show(
                display_meta["display"].output, self.render_view
            )
            for k, v in display_meta["repr_props"].items():
                representation.__setattr__(k, v)

    def set_chromosome(self, chromosome: str, experiment: str, timestep: str):
        self._chromosome = chromosome
        self._experiment = experiment
        self._timestep = timestep

    def add_structure_display(self, display_type: str, point_spacing: int):
        source_key = "structure_structure"
        structure_source_meta = self._sources.get(source_key)

        if structure_source_meta is None:
            structure = self._source.get_structure(
                self._chromosome, self._experiment, self._timestep
            )
            structure_indices = [p["index"] for p in structure]
            structure_source = StructureSource()
            structure_source.set_splines(self._splines)
            structure_source.set_data(structure_indices, point_spacing)
            structure_source_meta = {
                "source": structure_source,
                "source_name": "structure",
                "source_type": "structure",
            }

            self._sources[source_key] = structure_source_meta

        structure_source = structure_source_meta["source"]

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

        display_id = self._display_id
        self._display_id += 1

        self._displays[display_id] = {
            "enabled": True,
            "track_name": "structure",
            "track_type": "structure",
            "display": display,
            "representation": representation,
            "repr_props": repr_props,
        }

        return display_id

    def add_peak_display(self, track_name: str, display_type: str, point_spacing: int):
        source_key = f"peak_{track_name}"
        peak_source_meta = self._sources.get(source_key)

        if peak_source_meta is None:
            track = self._source.get_peak_track(
                self._chromosome, self._experiment, self._timestep, track_name
            )
            track_source = PeakTrackSource()
            track_source.set_splines(self._splines)
            track_source.set_data(track, point_spacing)
            peak_source_meta = {
                "source": track_source,
                "source_name": "structure",
                "source_type": track_name,
            }

            self._sources[source_key] = peak_source_meta

        track_source = peak_source_meta["source"]

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

        display_id = self._display_id
        self._display_id += 1

        self._displays[display_id] = {
            "enabled": True,
            "track_name": track_name,
            "track_type": "peak",
            "display": display,
            "representation": representation,
            "repr_props": repr_props,
        }

        return display_id

    def add_point_display(self, track_name: str, display_type: str, point_spacing: int):
        source_key = f"point_{track_name}"
        point_source_meta = self._sources.get(source_key)

        if point_source_meta is None:
            track = self._source.get_point_track(
                self._chromosome, self._experiment, self._timestep, track_name
            )
            track_source = PointTrackSource()
            track_source.set_splines(self._splines)
            track_source.set_data(track, point_spacing)
            point_source_meta = {
                "source": track_source,
                "source_name": "point",
                "source_type": track_name,
            }

            self._sources[source_key] = point_source_meta

        track_source = point_source_meta["source"]

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

        display_id = self._display_id
        self._display_id += 1

        self._displays[display_id] = {
            "enabled": True,
            "track_name": track_name,
            "track_type": "point",
            "display": display,
            "representation": representation,
            "repr_props": repr_props,
        }

        return display_id

    def modify_display(self, display_id: int, variable: str, display_type: str):
        raise NotImplementedError

    def remove_all_displays(self):
        for display_meta in self._displays.values():
            simple.Hide(display_meta["display"].output)
            simple.Delete(display_meta["representation"])
            simple.Delete(display_meta["display"].output)

        self._displays = {}

        for source_meta in self._sources.values():
            simple.Delete(source_meta["source"].output)

        self._sources = {}

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
