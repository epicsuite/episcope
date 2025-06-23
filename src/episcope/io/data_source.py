from typing import TypedDict

from paraview import simple

from episcope.io.interpolation_filter import INTERPOLATION_FILTER_SOURCE

class DataVariable(TypedDict):
    """A dictionary representing a time step with a time and a label.

    Attributes:
        name (str): The name of the time step.
        label (str): The label associated with the time step.
    """
    name: str
    label: str

ID_COLUMN = "id"
X_COLUMN = "x"
Y_COLUMN = "y"
Z_COLUMN = "z"
ARRAY_NAMES_TO_IGNORE = set((ID_COLUMN, X_COLUMN, Y_COLUMN, Z_COLUMN))

class DataSource:
    """A class to handle data from a file source.

    Attributes:
        file_path (str): The path to the file that contains the data.
    """

    def __init__(self, file_path: str) -> None:
        """Initializes the DataSource with a file path.

        Args:
            file_path (str): The path to the file that contains the data.
        """
        self.file_path = file_path
        self._reader = simple.CSVReader(FileName=[file_path])
        self._points = simple.TableToPoints(Input=self._reader)
        self._points.XColumn = X_COLUMN
        self._points.YColumn = Y_COLUMN
        self._points.ZColumn = Z_COLUMN
        self._points.KeepAllDataArrays = 1
        self._interpolation_filter = simple.ProgrammableFilter(Input=self._points)
        self._interpolation_filter.Script = INTERPOLATION_FILTER_SOURCE
        self._interpolation_filter.RequestInformationScript = ''
        self._interpolation_filter.RequestUpdateExtentScript = ''
        self._interpolation_filter.PythonPath = ''

        self._variables: list[DataVariable] = []
        self._discover_variables()

    @property
    def output(self):
        return self._interpolation_filter

    @property
    def variables(self) -> list[DataVariable]:
        return self._variables

    def _discover_variables(self):
        self._variables = []
        for i in range(self._points.PointData.NumberOfArrays):
            array = self._points.PointData.GetArray(i)
            name = array.Name

            if name in ARRAY_NAMES_TO_IGNORE:
                continue

            self._variables.append({"name": name, "label": name})
