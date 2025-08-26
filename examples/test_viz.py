from __future__ import annotations

DATA_DIRECTORY = (
    "/Users/alessandro.genova/work/sources/epicsuite/test_data/LA-UR-25-24911.1"
)


def test_viz():
    from paraview import simple

    from episcope.library.io.v1_1 import SourceProvider
    from episcope.library.io.v1_1.ensemble import Ensemble
    from episcope.library.viz.visualization import Visualization

    ensemble = Ensemble(DATA_DIRECTORY)
    source = SourceProvider(ensemble)

    render_view = simple.CreateView("RenderView")
    visualization = Visualization(source, render_view)

    experiment_name = "Untr_A"
    timestep_name = "12hpi"
    chromosome_name = "NC_023642.1"
    peak_track_name = "ATAC"
    point_track_name = "compartment"

    visualization.set_chromosome(chromosome_name, experiment_name, timestep_name)

    visualization.add_structure_display("tube", 10_000)
    visualization.add_structure_display("delaunay", -1)
    visualization.add_peak_display(peak_track_name, "tube", -1)
    visualization.add_point_display(point_track_name, "upper_gaussian_contour", -1)
    visualization.add_point_display(point_track_name, "lower_gaussian_contour", -1)

    simple.Interact(render_view)

    assert True


def main():
    test_viz()


if __name__ == "__main__":
    main()
