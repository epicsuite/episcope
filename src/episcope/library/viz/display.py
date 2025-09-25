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
            0.7796000000000001,
            0.007843,
            0.219608,
            0.345098,
            314.455683998,
            0.01178,
            0.286536,
            0.449427,
            628.1317679959999,
            0.015702,
            0.35328,
            0.553479,
            941.8103516042,
            0.01767,
            0.396586,
            0.622376,
            1255.4864356022001,
            0.021115,
            0.4402,
            0.690688,
            1569.1625196002,
            0.11757,
            0.503191,
            0.722184,
            1882.8386035982,
            0.214625,
            0.565859,
            0.753633,
            2196.5146875962,
            0.336671,
            0.615071,
            0.78316,
            2510.1921963720138,
            0.457978,
            0.663975,
            0.812503,
            2823.8693552024,
            0.556401,
            0.703345,
            0.836125,
            3137.5454392004,
            0.65421,
            0.742714,
            0.859669,
            3451.2215231984,
            0.736886,
            0.782084,
            0.881323,
            3764.8976071964003,
            0.81827,
            0.821638,
            0.903068,
            4078.5761908045997,
            0.873387,
            0.864944,
            0.92669,
            4392.2522748026,
            0.927536,
            0.907605,
            0.949988,
            4705.9283588006,
            0.964937,
            0.9391,
            0.967705,
            5000.0,
            1.0,
            0.968627,
            0.984314,
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
        else:
            self._output.VaryRadius = "Off"

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._output.Input = value
        self._output.Vectors = ["POINTS", "1"]
        self._output.NumberofSides = 30
        self._output.Radius = 0.05
        if self.variable != "":
            self._output.VaryRadius = "By Scalar"
        else:
            self._output.VaryRadius = "Off"
        self._output.RadiusFactor = 10.0

    @Display.representation_properties.getter
    def representation_properties(self):
        variable_properties = {}

        if self.variable == "":
            variable_properties["ColorArrayName"] = [None, ""]
            variable_properties["AmbientColor"] = [
                0.00784313725490196,
                0.2196078431372549,
                0.34509803921568627,
            ]
            variable_properties["DiffuseColor"] = [
                0.00784313725490196,
                0.2196078431372549,
                0.34509803921568627,
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
            "Opacity": 0.3,
        }


class UpperGaussianContourDisplay(GaussianContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.UpperThreshold = 1

    @property
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.3333333333333333, 0.0, 1.0],
            "DiffuseColor": [0.3333333333333333, 0.0, 1.0],
        }


class LowerGaussianContourDisplay(GaussianContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.LowerThreshold = -1.0

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.0, 0.3333333333333333, 0.0],
            "DiffuseColor": [0.0, 0.3333333333333333, 0.0],
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
