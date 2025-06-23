from paraview import simple


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
        self.lut.RGBPoints = [0.0, 0.031373, 0.188235, 0.419608, 2.00784, 0.031373, 0.253195, 0.516063, 4.01568, 0.031757, 0.318139, 0.612149, 6.023536, 0.080969, 0.38113, 0.661361, 8.031376, 0.130427, 0.444152, 0.710327, 10.039216, 0.195386, 0.509112, 0.743791, 12.047056, 0.260715, 0.573841, 0.777209, 14.054896, 0.341423, 0.628958, 0.808704, 16.06274512, 0.422745, 0.684075, 0.839892, 18.070592, 0.523137, 0.739193, 0.861546, 20.078432, 0.622684, 0.793464, 0.883429, 22.086272, 0.701423, 0.826928, 0.910988, 24.094112000000003, 0.778685, 0.8603, 0.937993, 26.101968, 0.825928, 0.891795, 0.953741, 28.109807999999997, 0.87328, 0.923291, 0.969489, 30.117648000000003, 0.922491, 0.954787, 0.985236, 32.0, 0.968627, 0.984314, 1.0]
        self.lut.ColorSpace = 'Lab'
        self.lut.NanColor = [1.0, 0.0, 0.0]
        self.lut.ScalarRangeInitialized = 1.0

    @Display.variable.setter
    def variable(self, value):
        self._variable = value

        self._output.Scalars = ['POINTS', value]

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._output.Input = value
        self._output.Vectors = ['POINTS', '1']
        self._output.NumberofSides = 12
        self._output.Radius = 0.05
        self._output.VaryRadius = 'By Scalar'
        self._output.RadiusFactor = 7.0

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": 'Surface',
            "ColorArrayName": ['POINTS', self.variable],
            "LookupTable": self.lut,
            "Specular": 1.0,
            "SpecularPower": 50.0,
            "SelectNormalArray": 'TubeNormals',
            "SelectTangentArray": 'None',
            "SelectTCoordArray": 'None',
            "TextureTransform": 'Transform2',
            "OSPRayScaleArray": 'TubeNormals',
            "OSPRayScaleFunction": 'Piecewise Function',
            "Assembly": '',
            "SelectedBlockSelectors": [''],
            "SelectOrientationVectors": 'None',
            "ScaleFactor": 0.987163782119751,
            "SelectScaleArray": 'None',
            "GlyphType": 'Arrow',
            "GlyphTableIndexArray": 'None',
            "GaussianRadius": 0.04935818910598755,
            "SetScaleArray": ['POINTS', 'TubeNormals'],
            "ScaleTransferFunction": 'Piecewise Function',
            "OpacityArray": ['POINTS', 'TubeNormals'],
            "OpacityTransferFunction": 'Piecewise Function',
            "DataAxesGrid": 'Grid Axes Representation',
            "PolarAxes": 'Polar Axes Representation',
            "SelectInputVectors": ['POINTS', 'TubeNormals'],
            "WriteLog": '',
        }

class ContourDisplay(Display):
    def __init__(self):
        super().__init__()
        self._glyph = simple.Glyph(GlyphType='2D Glyph')
        self._glyph.OrientationArray = ['POINTS', 'No orientation array']
        self._glyph.ScaleArray = ['POINTS', 'No scale array']
        self._glyph.ScaleFactor = 0.5416259999999999
        self._glyph.GlyphTransform = 'Transform2'
        self._glyph.GlyphMode = 'All Points'

        self._threshold = simple.Threshold(Input=self._glyph)

        self._gaussian = simple.GaussianResampling(Input=self._threshold)
        self._gaussian.ResampleField = ['POINTS', 'ignore arrays']
        self._gaussian.ResamplingGrid = [100, 100, 100]
        self._gaussian.ExtenttoResample = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
        self._gaussian.ScaleSplats = 0
        self._gaussian.EllipticalSplats = 0
        self._gaussian.SplatAccumulationMode = 'Sum'

        self._output = simple.Contour(Input=self._gaussian)
        self._output.ContourBy = ['POINTS', 'SplatterValues']
        self._output.Isosurfaces = [20.0]
        self._output.PointMergeMethod = 'Uniform Binning'

    @Display.variable.setter
    def variable(self, value):
        self._variable = value

        self._threshold.Scalars = ['POINTS', value]

    @Display.input.setter
    def input(self, value):
        self._input = value

        self._glyph.Input = value

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": 'Surface',
            "ColorArrayName": ['POINTS', ''],
            "Opacity": 0.3,
            "SelectNormalArray": 'Normals',
            "SelectTangentArray": 'None',
            "SelectTCoordArray": 'None',
            "TextureTransform": 'Transform2',
            "OSPRayScaleArray": 'SplatterValues',
            "OSPRayScaleFunction": 'Piecewise Function',
            "Assembly": '',
            "SelectedBlockSelectors": [''],
            "SelectOrientationVectors": 'None',
            "SelectScaleArray": 'SplatterValues',
            "GlyphType": 'Arrow',
            "GlyphTableIndexArray": 'SplatterValues',
            "SetScaleArray": ['POINTS', 'SplatterValues'],
            "ScaleTransferFunction": 'Piecewise Function',
            "OpacityArray": ['POINTS', 'SplatterValues'],
            "OpacityTransferFunction": 'Piecewise Function',
            "DataAxesGrid": 'Grid Axes Representation',
            "PolarAxes": 'Polar Axes Representation',
            "SelectInputVectors": ['POINTS', 'Normals'],
            "WriteLog": '',
        }

class UpperContourDisplay(ContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.UpperThreshold = 1.0

    @property
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.7490196078431373, 0.5294117647058824, 1.0],
            "DiffuseColor": [0.7490196078431373, 0.5294117647058824, 1.0],
            "ScaleFactor": 0.7444028854370117,
            "GaussianRadius": 0.03722014427185059,
        }

class LowerContourDisplay(ContourDisplay):
    def __init__(self):
        super().__init__()

        self._threshold.LowerThreshold = -1.0

    @property
    def representation_properties(self):
        return {
            **super().representation_properties,
            "AmbientColor": [0.0, 0.6666666666666666, 0.0],
            "DiffuseColor": [0.0, 0.6666666666666666, 0.0],
            "ScaleFactor": 0.9418681621551515,
            "GaussianRadius": 0.04709340810775757,
        }