from paraview import simple

from episcope.io.directory_provider import DirectoryProvider
from episcope.io.data_source import DataSource
from episcope.io.display import Display, TubeDisplay, UpperContourDisplay, LowerContourDisplay

class Visualization:
    """A class responsible for visualizing data from a directory using a render view.

    Attributes:
        directory_provider (DirectoryProvider): An instance of DirectoryProvider to access the data files.
        render_view (RenderView): The RenderView this visualization will draw to.
        _dataset_timestamp (tuple[str, str]): A combined index of a dataset and a timestamp
    """

    def __init__(self, directory_provider: DirectoryProvider, render_view) -> None:
        """Initializes the Visualization with a DirectoryProvider and a RenderView.

        Args:
            directory_provider (DirectoryProvider): The provider to get directory paths.
            render_view (RenderView): The renderer to display the data.
        """
        self.directory_provider = directory_provider
        self.render_view = render_view
        self._dataset_timestamp: tuple[str, str] = ("", "")
        self._source: DataSource | None = None
        self._displays: dict[int, Display] = {}
        self._display_id = 0

    def set_source(self, dataset: str, timestep: str):
        data_file = self.directory_provider.get_data_file(dataset, timestep)
        self._source = DataSource(data_file)

        for display in self._displays.values():
            display.input = self._source.output

    def add_display(self, variable: str, display_type: str) -> int:
        display_id = self._display_id
        self._display_id += 1

        if display_type == "tube":
            display = TubeDisplay()
        elif display_type == "upper_contour":
            display = UpperContourDisplay()
        elif display_type == "lower_contour":
            display = LowerContourDisplay()
        else:
            raise ValueError(f"Unknown display type: '{display_type}'")

        display.input = self._source.output
        display.variable = variable

        representation = simple.Show(display.output, self.render_view)
        for k, v in display.representation_properties.items():
            representation.__setattr__(k, v)

        return display_id

    def modify_display(self, display_id: int, variable: str, display_type: str):
        pass

    def remove_display(self, display_id: int):
        pass
