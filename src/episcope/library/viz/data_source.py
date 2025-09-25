from __future__ import annotations

from paraview import simple
from vtkmodules.vtkCommonCore import vtkFloatArray, vtkPoints, vtkStringArray
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolyLine
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter

from episcope.library.io import LabelPoint, PeakTrackPoint, PointTrackPoint
from episcope.library.viz.common import CardinalSplines


class DataSource:
    """Abstract base class for a datasource of the visualization pipeline."""

    def update(self):
        raise NotImplementedError

    @property
    def output(self):
        """Get the output paraview filter for this data source.

        Returns:
            The output data object that can be used for visualization.

        Raises:
            NotImplementedError: This is an abstract method that must be
                implemented by subclasses.
        """
        raise NotImplementedError


class StructureSource(DataSource):
    """Data source for chromosome structure visualization.

    This class handles the creation of 3D structure data from genomic coordinates
    using cardinal splines for smooth curve representation.
    """

    def __init__(self):
        """Initialize the StructureSource with default values."""
        self._data = None
        self._max_distance = -1
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    def update(self):
        self.set_data(self._data, self._max_distance)

    @property
    def output(self):
        """Get the output VTK data object for the structure.

        Returns:
            The TrivialProducer containing the structure data as vtkPolyData.
        """
        return self._output

    def set_splines(self, splines: CardinalSplines):
        """Set the cardinal splines for 3D coordinate interpolation.

        Args:
            splines: A dictionary containing x, y, and z splines for coordinate
                interpolation.
        """
        self._splines = splines

    def set_data(self, data: list[int], max_distance: int):
        """Set the structure data and generate VTK polydata for visualization.

        This method processes genomic indices to create a smooth 3D curve representation
        using cardinal splines. If max_distance is positive, it interpolates points
        between consecutive indices.

        Args:
            data: A list of base pair indices representing the chromosome structure.
            max_distance: The maximum distance between interpolated points. If <= 0,
                no interpolation occurs and all original points are used.

        Raises:
            RuntimeError: If splines have not been set before calling this method.
        """
        if self._splines is None:
            msg = "splines should be set before setting source data."
            raise RuntimeError(msg)

        self._data = data
        self._max_distance = max_distance

        polydata = vtkPolyData()
        points = vtkPoints()
        line = vtkPolyLine()
        cells = vtkCellArray()

        if max_distance <= 0 or len(data) < 2:
            indices = data
        else:
            indices = []
            for i in range(len(data) - 1):
                index = data[i]
                while index < data[i + 1]:
                    indices.append(index)
                    index += max_distance

        points.SetNumberOfPoints(len(indices))
        line.GetPointIds().SetNumberOfIds(len(indices))

        x_spline = self._splines["x"]
        y_spline = self._splines["y"]
        z_spline = self._splines["z"]

        for i, index in enumerate(indices):
            points.SetPoint(
                i,
                (
                    x_spline.Evaluate(index),
                    y_spline.Evaluate(index),
                    z_spline.Evaluate(index),
                ),
            )
            line.GetPointIds().SetId(i, i)

        cells.InsertNextCell(line)

        # Set points, cells (lines), and point data to the output vtkPolyData
        polydata.SetPoints(points)
        polydata.SetLines(cells)

        self._output.GetClientSideObject().SetOutput(polydata)


class PeakTrackSource(DataSource):
    """Data source for peak track visualization.

    This class handles the creation of 3D peak track data from genomic coordinates
    using cardinal splines for smooth curve representation.
    """

    def __init__(self):
        """Initialize the PeakTrackSource with default values."""
        self._data = None
        self._max_distance = -1
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    def update(self):
        self.set_data(self._data, self._max_distance)

    @property
    def output(self):
        """Get the output VTK data object for the peak track.

        Returns:
            The TrivialProducer containing the peak track data as vtkPolyData.
        """
        return self._output

    def set_splines(self, splines: CardinalSplines):
        """Set the cardinal splines for 3D coordinate interpolation.

        Args:
            splines: A dictionary containing x, y, and z splines for coordinate
                interpolation.
        """
        self._splines = splines

    def set_data(self, data: list[PeakTrackPoint], max_distance: int):
        """Set the peak track data and generate VTK polydata for visualization.

        This method processes peak track points to create a 3D representation
        using cardinal splines. Each peak is represented as a triangle with
        start point (0), summit point (with value), and end point (0).

        Args:
            data: A list of PeakTrackPoint objects containing peak information.
            max_distance: The maximum distance between interpolated points. If <= 0,
                no interpolation occurs and all original points are used.

        Raises:
            RuntimeError: If splines have not been set before calling this method.
        """
        if self._splines is None:
            msg = "splines should be set before setting source data."
            raise RuntimeError(msg)

        self._data = data
        self._max_distance = max_distance

        polydata = vtkPolyData()
        points = vtkPoints()
        cells = vtkCellArray()
        pointdata = polydata.GetPointData()
        array = vtkFloatArray()

        interpolated_data: list[list[tuple[int, float]]] = []
        n_points = 0

        if max_distance <= 0:
            for peak_point in data:
                n_points += 3
                interpolated_data.append(
                    [
                        (peak_point["start"], 0),
                        (peak_point["summit"], peak_point["value"]),
                        (peak_point["end"], 0),
                    ]
                )
        else:
            pass

        x_spline = self._splines["x"]
        y_spline = self._splines["y"]
        z_spline = self._splines["z"]

        points.SetNumberOfPoints(n_points)
        point_id = 0

        array.SetName("scalars")
        array.SetNumberOfTuples(n_points)
        array.SetNumberOfComponents(1)

        for segment in interpolated_data:
            cells.InsertNextCell(len(segment))
            for index, value in segment:
                points.SetPoint(
                    point_id,
                    (
                        x_spline.Evaluate(index),
                        y_spline.Evaluate(index),
                        z_spline.Evaluate(index),
                    ),
                )
                cells.InsertCellPoint(point_id)
                array.SetTuple1(point_id, value)

                point_id += 1

        polydata.SetPoints(points)
        polydata.SetLines(cells)
        pointdata.AddArray(array)

        self._output.GetClientSideObject().SetOutput(polydata)


class PointTrackSource(DataSource):
    """Data source for point track visualization.

    This class handles the creation of 3D point track data from genomic coordinates
    using cardinal splines for smooth curve representation.
    """

    def __init__(self):
        """Initialize the PointTrackSource with default values."""
        self._data = None
        self._max_distance = -1
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    def update(self):
        self.set_data(self._data, self._max_distance)

    @property
    def output(self):
        """Get the output VTK data object for the point track.

        Returns:
            The TrivialProducer containing the point track data as vtkPolyData.
        """
        return self._output

    def set_splines(self, splines: CardinalSplines):
        """Set the cardinal splines for 3D coordinate interpolation.

        Args:
            splines: A dictionary containing x, y, and z splines for coordinate
                interpolation.
        """
        self._splines = splines

    def set_data(self, data: list[PointTrackPoint], max_distance: int):
        """Set the point track data and generate VTK polydata for visualization.

        This method processes point track data to create a 3D representation
        using cardinal splines. Points are interpolated between start and end
        positions based on max_distance parameter.

        Args:
            data: A list of PointTrackPoint objects containing point track information.
            max_distance: The maximum distance between interpolated points. If <= 0,
                no interpolation occurs and only start/end points are used.

        Raises:
            RuntimeError: If splines have not been set before calling this method.
        """
        if self._splines is None:
            msg = "splines should be set before setting source data."
            raise RuntimeError(msg)

        self._data = data
        self._max_distance = max_distance

        polydata = vtkPolyData()
        points = vtkPoints()
        cells = vtkCellArray()
        pointdata = polydata.GetPointData()
        array = vtkFloatArray()

        interpolated_data: list[list[tuple[int, float]]] = []
        n_points = 0

        if max_distance <= 0:
            for track_point in data:
                n_points += 2
                interpolated_data.append(
                    [
                        (track_point["start"], track_point["value"]),
                        (track_point["end"], track_point["value"]),
                    ]
                )
        else:
            for track_point in data:
                index = track_point["start"]
                segment = []
                while index < track_point["end"]:
                    segment.append((index, track_point["value"]))
                    n_points += 1
                    index += max_distance
                segment.append((track_point["end"], track_point["value"]))
                n_points += 1
                interpolated_data.append(segment)

        x_spline = self._splines["x"]
        y_spline = self._splines["y"]
        z_spline = self._splines["z"]

        points.SetNumberOfPoints(n_points)
        point_id = 0

        array.SetName("scalars")
        array.SetNumberOfTuples(n_points)
        array.SetNumberOfComponents(1)

        # cells.InsertNextCell(n_points)
        for segment in interpolated_data:
            cells.InsertNextCell(len(segment))
            for index, value in segment:
                points.SetPoint(
                    point_id,
                    (
                        x_spline.Evaluate(index),
                        y_spline.Evaluate(index),
                        z_spline.Evaluate(index),
                    ),
                )
                cells.InsertCellPoint(point_id)
                array.SetTuple1(point_id, value)

                point_id += 1

        polydata.SetPoints(points)
        polydata.SetLines(cells)
        pointdata.AddArray(array)

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName("compartment_point_track.vtp")
        writer.SetInputData(polydata)
        writer.Write()

        self._output.GetClientSideObject().SetOutput(polydata)


class LabelTrackSource(DataSource):
    def __init__(self):
        """Initialize the LabelTrackSource with default values."""
        self._data = None
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    def update(self):
        self.set_data(self._data, -1)

    @property
    def output(self):
        """Get the output VTK data object for the peak track.

        Returns:
            The TrivialProducer containing the peak track data as vtkPolyData.
        """
        return self._output

    def set_splines(self, splines: CardinalSplines):
        """Set the cardinal splines for 3D coordinate interpolation.

        Args:
            splines: A dictionary containing x, y, and z splines for coordinate
                interpolation.
        """
        self._splines = splines

    def set_data(self, data: list[LabelPoint], _max_distance: int):
        """Set the peak track data and generate VTK polydata for visualization.

        This method processes peak track points to create a 3D representation
        using cardinal splines. Each peak is represented as a triangle with
        start point (0), summit point (with value), and end point (0).

        Args:
            data: A list of PeakTrackPoint objects containing peak information.
            max_distance: The maximum distance between interpolated points. If <= 0,
                no interpolation occurs and all original points are used.

        Raises:
            RuntimeError: If splines have not been set before calling this method.
        """
        if self._splines is None:
            msg = "splines should be set before setting source data."
            raise RuntimeError(msg)

        self._data = data

        polydata = vtkPolyData()
        points = vtkPoints()
        pointdata = polydata.GetPointData()

        labels = vtkStringArray(name="labels")
        labels.SetNumberOfValues(len(data))
        points.SetNumberOfPoints(len(data))

        x_spline = self._splines["x"]
        y_spline = self._splines["y"]
        z_spline = self._splines["z"]

        for i, label_point in enumerate(data):
            points.SetPoint(
                i,
                (
                    x_spline.Evaluate(label_point["index"]),
                    y_spline.Evaluate(label_point["index"]),
                    z_spline.Evaluate(label_point["index"]),
                ),
            )
            labels.SetValue(i, label_point["text"])

        polydata.SetPoints(points)
        pointdata.AddArray(labels)

        self._output.GetClientSideObject().SetOutput(polydata)
