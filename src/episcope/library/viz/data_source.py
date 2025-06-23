from typing import TypedDict

from paraview import simple

from episcope.library.io import PointTrackPoint, PeakTrackPoint
from episcope.library.viz.common import CardinalSplines
from vtkmodules.vtkCommonCore import vtkPoints, vtkFloatArray
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray, vtkPolyLine
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter

class DataSource:
    @property
    def output(self):
        raise NotImplementedError

class StructureSource(DataSource):
    def __init__(self):
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    @property
    def output(self):
        return self._output

    def set_splines(self, splines: CardinalSplines):
        self._splines = splines

    def set_data(self, data: list[int], max_distance: int):
        if self._splines is None:
            raise RuntimeError("splines should be set before setting source data.")

        polydata = vtkPolyData()
        points = vtkPoints()
        line = vtkPolyLine()
        cells = vtkCellArray()
        pointdata = polydata.GetPointData()

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
            points.SetPoint(i, (x_spline.Evaluate(index), y_spline.Evaluate(index), z_spline.Evaluate(index)))
            line.GetPointIds().SetId(i, i)

        cells.InsertNextCell(line)

        # Set points, cells (lines), and point data to the output vtkPolyData
        polydata.SetPoints(points)
        polydata.SetLines(cells)

        self._output.GetClientSideObject().SetOutput(polydata)



class PeakTrackSource(DataSource):
    def __init__(self):
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    @property
    def output(self):
        return self._output

    def set_splines(self, splines: CardinalSplines):
        self._splines = splines

    def set_data(self, data: list[PeakTrackPoint], max_distance: int):
        if self._splines is None:
            raise RuntimeError("splines should be set before setting source data.")

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
                interpolated_data.append([
                    (peak_point["start"], 0),
                    (peak_point["summit"], peak_point["value"]),
                    (peak_point["end"], 0),
                ])
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
            for i, (index, value) in enumerate(segment):
                points.SetPoint(point_id, (x_spline.Evaluate(index), y_spline.Evaluate(index), z_spline.Evaluate(index)))
                cells.InsertCellPoint(point_id)
                array.SetTuple1(point_id, value)

                point_id += 1

        polydata.SetPoints(points)
        polydata.SetLines(cells)
        pointdata.AddArray(array)

        self._output.GetClientSideObject().SetOutput(polydata)


class PointTrackSource(DataSource):
    def __init__(self):
        self._splines: CardinalSplines | None = None
        self._output = simple.TrivialProducer()

    @property
    def output(self):
        return self._output

    def set_splines(self, splines: CardinalSplines):
        self._splines = splines

    def set_data(self, data: list[PointTrackPoint], max_distance: int):
        if self._splines is None:
            raise RuntimeError("splines should be set before setting source data.")

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
                interpolated_data.append([
                    (track_point["start"], track_point["value"]),
                    (track_point["end"], track_point["value"]),
                ])
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
            for i, (index, value) in enumerate(segment):
                points.SetPoint(point_id, (x_spline.Evaluate(index), y_spline.Evaluate(index), z_spline.Evaluate(index)))
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


# class DataSource:
#     """A class to handle data from a file source.

#     Attributes:
#         file_path (str): The path to the file that contains the data.
#     """

#     def __init__(self, file_path: str) -> None:
#         """Initializes the DataSource with a file path.

#         Args:
#             file_path (str): The path to the file that contains the data.
#         """
#         self.file_path = file_path
#         self._reader = simple.CSVReader(FileName=[file_path])
#         self._points = simple.TableToPoints(Input=self._reader)
#         self._points.XColumn = X_COLUMN
#         self._points.YColumn = Y_COLUMN
#         self._points.ZColumn = Z_COLUMN
#         self._points.KeepAllDataArrays = 1
#         self._interpolation_filter = simple.ProgrammableFilter(Input=self._points)
#         self._interpolation_filter.Script = INTERPOLATION_FILTER_SOURCE
#         self._interpolation_filter.RequestInformationScript = ''
#         self._interpolation_filter.RequestUpdateExtentScript = ''
#         self._interpolation_filter.PythonPath = ''

#         self._variables: list[DataVariable] = []
#         self._discover_variables()

#     @property
#     def output(self):
#         return self._interpolation_filter

#     @property
#     def variables(self) -> list[DataVariable]:
#         return self._variables

#     def _discover_variables(self):
#         self._variables = []
#         for i in range(self._points.PointData.NumberOfArrays):
#             array = self._points.PointData.GetArray(i)
#             name = array.Name

#             if name in ARRAY_NAMES_TO_IGNORE:
#                 continue

#             self._variables.append({"name": name, "label": name})
