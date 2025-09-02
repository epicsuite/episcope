from __future__ import annotations

import numpy as np

from episcope.library.io import StructurePoint


def compute_similarity_transform(A: np.ndarray, B: np.ndarray):
    """
    Compute the similarity transformation (s, R, t) that best aligns each point in A
    to the corresponding point in B, including uniform scaling.
    """
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # Ensure a proper rotation by enforcing a right-handed coordinate system
    if np.linalg.det(R) < 0:
        Vt[2, :] *= -1
        R = np.dot(Vt.T, U.T)

    # Compute scaling
    # scale = np.sum(S) / np.sum(AA ** 2) # Umeyama
    # scale = (np.sum(BB ** 2) / np.sum(AA ** 2))**0.5 # wiki
    scale = 1  # no scale change

    # Compute translation
    t = centroid_B - scale * np.dot(R, centroid_A)

    return scale, R, t


def apply_similarity_transformation(points, s, R, t):
    """
    Apply the computed similarity transformation (s, R, t) to the points.
    """
    return s * np.dot(points, R.T) + t


def align_structures(A: list[StructurePoint], B: list[StructurePoint], n_samples: int):
    n_samples = min(n_samples, len(A), len(B))

    A_spacing = len(A) // n_samples
    A_sampled = A[slice(0, A_spacing * n_samples, A_spacing)]
    B_spacing = len(B) // n_samples
    B_sampled = B[slice(0, B_spacing * n_samples, B_spacing)]

    assert len(A_sampled) == n_samples
    assert len(B_sampled) == n_samples

    A_positions = np.array([point["position"] for point in A])
    A_sampled_positions = np.array([point["position"] for point in A_sampled])
    B_sampled_positions = np.array([point["position"] for point in B_sampled])

    # Compute the similarity transformation
    scale, R, t = compute_similarity_transform(A_sampled_positions, B_sampled_positions)

    # Apply the transformation to A's positions
    transformed_A_positions = apply_similarity_transformation(A_positions, scale, R, t)

    transformed_A: list[StructurePoint] = []
    for structure_point, transformed_point in zip(
        A, transformed_A_positions, strict=False
    ):
        transformed_A.append(
            {"index": structure_point["index"], "position": tuple(transformed_point)}
        )

    return transformed_A
