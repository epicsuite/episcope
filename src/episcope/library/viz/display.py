from __future__ import annotations

from paraview import simple
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkGlyph3DMapper,
)
from vtkmodules.vtkRenderingLabel import (
    vtkLabeledDataMapper,
)


class Display:
    def __init__(self):
        self._input = None
        self._output = None
        self._variable = ""

    @property
    def output(self):
        return self._output

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = value

    @property
    def variable(self):
        return self._variable

    @variable.setter
    def variable(self, value):
        self._variable = value

    @property
    def representation_properties(self):
        return {}


class TubeDisplay(Display):
    def __init__(self):
        super().__init__()
        self._output = simple.Tube()
        self.lut = simple.CreateLookupTable()
        self.lut.RGBPoints = [
			-0.247059,
			0.90551300000000001,
			0.163552,
			0.54293000000000002,
			-0.121569,
			0.88976500000000003,
			0.28166099999999999,
			0.61773199999999995,
			0.0039215700000000001,
			0.87315600000000004,
			0.39896999999999999,
			0.69161099999999998,
			0.129412,
			0.82984999999999998,
			0.49148799999999998,
			0.73688600000000004,
			0.25490200000000002,
			0.78908100000000003,
			0.58323700000000001,
			0.78185300000000002,
			0.38039200000000001,
			0.81073399999999995,
			0.65607099999999996,
			0.81925400000000004,
        ]
        self.lut.ColorSpace = "RGB"
        self.lut.ScalarRangeInitialized = 1.0
        self.variable = self._variable

    @Display.variable.setter
    def variable(self, value):
        self._variable = value

        self._output.Scalars = ["POINTS", value]

        if value != "":
            self._output.VaryRadius = "By Scalar"
            self._output.NumberofSides = 20
            self._output.Radius = 0.05
            self._output.RadiusFactor = 10.0
        else:
            self._output.VaryRadius = "Off"
            self._output.Radius = 0.035
            self._output.NumberofSides = 8

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._output.Input = value
        self._output.Vectors = ["POINTS", "1"]
        if self.variable != "":
            self._output.VaryRadius = "By Scalar"
        else:
            self._output.VaryRadius = "Off"

    @Display.representation_properties.getter
    def representation_properties(self):
        variable_properties = {}

        if self.variable == "":
            variable_properties["ColorArrayName"] = [None, ""]
            variable_properties["AmbientColor"] = [
                0.95,
                0.93,
                0.9,
            ]
            variable_properties["DiffuseColor"] = [
                0.95,
                0.93,
                0.9,
            ]
        else:
            variable_properties["ColorArrayName"] = ["POINTS", self.variable]
            variable_properties["LookupTable"] = (self.lut,)

        return {
            **variable_properties,
            "Representation": "Surface",
            "SelectNormalArray": "TubeNormals",
            "SelectTangentArray": "None",
            "SelectTCoordArray": "None",
            "TextureTransform": "Transform2",
            "OSPRayScaleArray": "TubeNormals",
            "OSPRayScaleFunction": "Piecewise Function",
            "Assembly": "",
            "SelectedBlockSelectors": [""],
            "SelectOrientationVectors": "None",
            "ScaleFactor": 1,
            "SelectScaleArray": "None",
            "GlyphType": "Arrow",
            "GlyphTableIndexArray": "None",
            "GaussianRadius": 0.04403236389160156,
            "SetScaleArray": ["POINTS", "TubeNormals"],
            "ScaleTransferFunction": "Piecewise Function",
            "OpacityArray": ["POINTS", "TubeNormals"],
            "OpacityTransferFunction": "Piecewise Function",
            "DataAxesGrid": "Grid Axes Representation",
            "PolarAxes": "Polar Axes Representation",
            "SelectInputVectors": ["POINTS", "TubeNormals"],
            "WriteLog": "",
        }


class GaussianContourDisplay(Display):
    def __init__(self):
        super().__init__()
        self._threshold = simple.Threshold()
        self._threshold.UpperThreshold = 0
        self._threshold.LowerThreshold = 0

        self._gaussian = simple.GaussianResampling(Input=self._threshold)
        self._gaussian.ResampleField = ["POINTS", "ignore arrays"]
        self._gaussian.SplatAccumulationMode = "Sum"

        self._output = simple.Contour(Input=self._gaussian)
        self._output.ContourBy = ["POINTS", "SplatterValues"]
        self._output.Isosurfaces = [1]
        self._output.PointMergeMethod = "Uniform Binning"

    @Display.variable.setter
    def variable(self, value):
        self._variable = value

        self._threshold.Scalars = ["POINTS", value]

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._threshold.Input = value

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": "Surface",
            "ColorArrayName": ["POINTS", ""],
            "Opacity": 0.25,
        }


class UpperGaussianContourDisplay(GaussianContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.UpperThreshold = 1

    @property
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.42, 0.80, 0.83],
            "DiffuseColor": [0.42, 0.80, 0.83],
        }


class LowerGaussianContourDisplay(GaussianContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.LowerThreshold = -1.0

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.99, 0.96, 0.44],
            "DiffuseColor": [0.99, 0.96, 0.44],
        }


class DelaunayDisplay(Display):
    def __init__(self):
        super().__init__()
        self._output = simple.Delaunay3D()

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._output.Input = value

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": "Surface",
            "ColorArrayName": [None, ""],
            "Opacity": 0.07,
        }


class VtkDisplay(Display):
    pass


class LabelsDisplay(VtkDisplay):
    def __init__(self):
        super().__init__()
        self._label_mapper = vtkLabeledDataMapper()
        self._label_mapper.SetLabelModeToLabelFieldData()
        self._label_mapper.SetFieldDataName("labels")

        self._output = vtkActor2D(mapper=self._label_mapper)

    @Display.input.setter
    def input(self, value):
        self._input = value
        self._input.GetClientSideObject() >> self._label_mapper


class SpheresDisplay(VtkDisplay):
    def __init__(self):
        super().__init__()
        self._sphere_source = vtkSphereSource(radius=0.1)
        self._point_mapper = vtkGlyph3DMapper(
            source_connection=self._sphere_source.output_port,
            scalar_visibility=False,
            scaling=False,
        )

        self._output = vtkActor(mapper=self._point_mapper)

    @Display.input.setter
    def input(self, value):
        self._input = value
        self._input.GetClientSideObject() >> self._point_mapper

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "color": [1, 1, 0],
        }
