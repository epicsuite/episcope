"""
Shared selection key objects to be imported
"""

from vtkmodules.vtkCommonCore import vtkInformationStringKey

SELECTION_OBJECT_ID = vtkInformationStringKey.MakeKey("SelectionObjectId", "Display")
SELECTION_OBJECT_KIND = vtkInformationStringKey.MakeKey("SelectionObjectKind", "Display")
