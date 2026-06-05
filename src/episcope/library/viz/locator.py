import numpy as np

from vtkmodules.util.numpy_support import vtk_to_numpy


def _vtk_matrix_to_numpy(m):
    return np.array(
        [[m.GetElement(r, c) for c in range(4)] for r in range(4)],
        dtype=np.float64,
    )


def _dataset_points_mtime(ds):
    pts = ds.GetPoints()
    if pts is None:
        return ds.GetMTime()

    arr = pts.GetData()
    return max(
        ds.GetMTime(),
        pts.GetMTime(),
        arr.GetMTime() if arr is not None else 0,
    )


def _project_points_to_display(renderer, points_xyz):
    """
    Vectorized world -> display projection for many points.

    Returns:
        display_xyz: (N, 3), where x/y are display pixels and z is 0..1-ish
        valid:       (N,) bool
    """
    camera = renderer.GetActiveCamera()

    aspect = renderer.GetTiledAspectRatio()

    # nearz=0, farz=1 means projected z maps to z-buffer-like coordinates.
    m = camera.GetCompositeProjectionTransformMatrix(aspect, 0.0, 1.0)
    mat = _vtk_matrix_to_numpy(m)

    n = points_xyz.shape[0]

    pts_h = np.empty((n, 4), dtype=np.float64)
    pts_h[:, :3] = points_xyz
    pts_h[:, 3] = 1.0

    clip = pts_h @ mat.T

    w = clip[:, 3]
    valid = np.abs(w) > 1e-12

    view = np.empty((n, 3), dtype=np.float64)
    view[:] = np.nan
    view[valid] = clip[valid, :3] / w[valid, None]

    # VTK view coords x/y are typically [-1, 1]; convert to display pixels.
    origin = renderer.GetOrigin()
    size = renderer.GetSize()

    display = np.empty((n, 3), dtype=np.float64)
    display[:, 0] = origin[0] + (view[:, 0] + 1.0) * 0.5 * size[0]
    display[:, 1] = origin[1] + (view[:, 1] + 1.0) * 0.5 * size[1]
    display[:, 2] = view[:, 2]

    # Keep points inside clipping depth.
    valid &= np.isfinite(display[:, 0])
    valid &= np.isfinite(display[:, 1])
    valid &= np.isfinite(display[:, 2])
    valid &= display[:, 2] >= 0.0
    valid &= display[:, 2] <= 1.0

    return display, valid
