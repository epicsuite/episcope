from __future__ import annotations

from typing import TypedDict

from vtkmodules.vtkCommonComputationalGeometry import vtkCardinalSpline


class CardinalSplines(TypedDict):
    x: vtkCardinalSpline
    y: vtkCardinalSpline
    z: vtkCardinalSpline
