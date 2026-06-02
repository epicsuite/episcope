from __future__ import annotations

from paraview import simple

# selection help
from episcope.library.viz.selection_keys import SELECTION_OBJECT_ID, SELECTION_OBJECT_KIND
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkSelection,
    vtkSelectionNode,
)
from vtkmodules.vtkCommonCore import vtkInformation

from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
)
from vtkmodules.vtkRenderingLabel import (
    vtkLabeledDataMapper,
)

def ensure_proxy(obj, name="WrappedVTK"):
    # Already a ParaView proxy
    if hasattr(obj, "SMProxy"):
        return obj

    # Raw VTK dataset/data object -> wrap it
    if isinstance(obj, vtkDataObject):
        src = simple.TrivialProducer(registrationName=name)
        src.GetClientSideObject().SetOutput(obj)
        src.UpdatePipeline()
        return src

    raise TypeError(f"Cannot convert object of type {type(obj)} to a ParaView proxy")

class Display:
    def __init__(self):
        self._input = None
        self._output = None
        self._variable = ""
        self._selection_metadata = {}

    @property
    def output(self):
        return self._output

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, value):
        self._ids = value

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

    def set_selection_metadata(self, **metadata):
        self._selection_metadata.update(metadata)

    def _apply_metadata_to_prop(self, prop):
        if prop is None:
            return

        keys = prop.GetPropertyKeys()
        if keys is None:
            keys = vtkInformation()
            prop.SetPropertyKeys(keys)

        object_id = self._selection_metadata.get("object_id")
        if object_id is not None:
            keys.Set(SELECTION_OBJECT_ID, str(object_id))

        object_kind = self._selection_metadata.get("object_kind")
        if object_kind is not None:
            keys.Set(SELECTION_OBJECT_KIND, str(object_kind))

    def attach_selection_metadata(self, representation=None):
        """
        Attach metadata to the render prop/actor used by selection.
        Call this after Show(...) and Render().
        """
        # ParaView/simple-backed displays: metadata goes on the actor owned by the representation
        if representation is not None:
            vtk_rep = representation.GetClientSideObject()
            if vtk_rep is None:
                return

            prop = None

            if hasattr(vtk_rep, "GetActiveRepresentation"):
                active = vtk_rep.GetActiveRepresentation()
                if active is not None and hasattr(active, "GetActor"):
                    prop = active.GetActor()

            if prop is None and hasattr(vtk_rep, "GetActor"):
                prop = vtk_rep.GetActor()

            if prop is None and hasattr(vtk_rep, "GetLODActor"):
                prop = vtk_rep.GetLODActor()

            self._apply_metadata_to_prop(prop)
            return

        # Raw VTK-backed displays: metadata goes directly on the actor
        if hasattr(self._output, "GetPropertyKeys") and hasattr(self._output, "SetPropertyKeys"):
            self._apply_metadata_to_prop(self._output)

class LineDisplay(Display):
    def __init__(self):
        super().__init__()
        self._output = None

    @Display.input.setter
    def input(self, value):
        self._input = value
        self._output = value  # no filter, just pass-through

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": "Wireframe",  # ensures line rendering
            "Opacity": 0.01,                # fully transparent
            "LineWidth": 1.0,              # irrelevant but harmless
        }

class TubeDisplay(Display):
    def __init__(self):
        super().__init__()
        self._output = simple.Tube()
        # colormap used for peak tubes
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

        # colormap used for rmsf
        self.rmsf_lut = simple.CreateLookupTable()
        self.rmsf_lut.RGBPoints = [
            0.700000,
            0.231373,
            0.298039,
            0.752941,

            0.775000,
            0.392157,
            0.529412,
            0.901961,

            0.850000,
            0.631373,
            0.760784,
            0.964706,

            0.925000,
            0.827451,
            0.894118,
            0.976471,

            1.000000,
            0.960784,
            0.960784,
            0.941176,

            1.050000,
            0.996078,
            0.878431,
            0.713725,

            1.100000,
            0.956863,
            0.611765,
            0.431373,

            1.150000,
            0.839216,
            0.321569,
            0.282353,

            1.200000,
            0.647059,
            0.000000,
            0.149020,
        ]
        self.rmsf_lut.ColorSpace = "RGB"
        self.rmsf_lut.ScalarRangeInitialized = 1.0

        self.variable = self._variable

    @Display.variable.setter
    def variable(self, value):
        self._variable = value

        self._output.Scalars = ["POINTS", value]

        if value != "" and value != "rmsf":
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
            if self.variable == "rmsf":
                variable_properties["LookupTable"] = (self.rmsf_lut,)
            else:
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

class SelectDisplay(Display):
    def __init__(self):
        super().__init__()

        self._input = None
        self._ids = None

        self._sel_node = vtkSelectionNode()
        self._sel_node.SetContentType(vtkSelectionNode.INDICES)
        self._sel_node.SetFieldType(vtkSelectionNode.POINT)

        self._sel = vtkSelection()
        self._sel.AddNode(self._sel_node)

        self._extract = vtkExtractSelection()
        self._extract.SetInputDataObject(1, self._sel)

        self._output = None
        self._repr = None

    @Display.input.setter
    def input(self, value):
        self._input = value
        self._extract.SetInputDataObject(0, value)
        self._update_output()

    @Display.ids.setter
    def ids(self, value):
        self._ids = value
        self._sel_node.SetSelectionList(value)
        self._update_output()

    def _update_output(self):
        if self._input is None:
            return

        self._extract.Update()
        extracted = self._extract.GetOutput()

        # Make a standalone copy so the shown proxy owns stable data.
        #copied = extracted.NewInstance()
        #copied.DeepCopy(extracted)

        # Recreate the producer instead of mutating an already-shown one.
        if self._output is not None:
            try:
                simple.Delete(self._output)
            except Exception:
                pass

        self._output = simple.TrivialProducer(registrationName="SelectDisplayOutput")
        self._output.GetClientSideObject().SetOutput(extracted)
        self._output.UpdatePipeline()

    @property
    def output(self):
        return self._output

    @Display.representation_properties.getter
    def representation_properties(self):
        return {
            "Representation": "Point Gaussian",
            "Opacity": 1,
            "GaussianRadius": 0.2,
            "DiffuseColor": [0, 1, 0],
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
