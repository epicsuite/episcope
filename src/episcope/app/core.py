from __future__ import annotations

from functools import partial

import numpy as np
import plotly.graph_objects as plotly_go
import plotly.subplots as plotly_subplots
from paraview import simple
from trame.app import get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import html, plotly
from trame.widgets import paraview as pv_widgets
from trame.widgets import vuetify3 as vuetify

from episcope.app.state import EpiscopeState, StateAdapterQuadrant3D
from episcope.library.io.v1_2 import Ensemble, SourceProvider
from episcope.library.viz.visualization import Visualization

# Possibly make it dynamic in the future
N_QUADRANTS_3D = 4
N_QUADRANTS_2D = N_QUADRANTS_3D


@TrameApp()
class App:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")

        self.server.cli.add_argument(
            "-d",
            "--data",
            help="Data directory to explore.",
            dest="data",
            required=True,
        )
        known_args, _ = self.server.cli.parse_known_args()
        self.context.data_directory = known_args.data

        self.context.pv_views = [None] * N_QUADRANTS_3D
        self.context.render_views = [None] * N_QUADRANTS_3D
        self.context.visualizations = [None] * N_QUADRANTS_3D
        self.context.plot_views = [None] * N_QUADRANTS_2D
        self.context.plot_figures = [None] * N_QUADRANTS_2D
        self.context.quadrants = {}

        simple.LoadPalette(paletteName="NeutralGrayBackground")
        palette = simple.GetSettingsProxy("ColorPalette")
        palette.Background = [0.784314, 0.784314, 0.784314]

        quadrants_3d = {}

        for i in range(N_QUADRANTS_3D):
            render_view = simple.CreateView("RenderView")
            quadrant = StateAdapterQuadrant3D(self.state, i)
            quadrant.chromosome = ""
            quadrant.experiment = ""
            quadrant.timestep = ""
            quadrants_3d[i] = quadrant
            self.context.render_views[i] = render_view

        self.context.quadrants_3d = quadrants_3d

        quadrants_2d = {}

        for i in range(N_QUADRANTS_2D):
            fig = plotly_subplots.make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(
                showlegend=False,
                # plot_bgcolor="white",
                margin={"t": 10, "l": 10, "b": 10, "r": 10},
            )
            self.context.plot_figures[i] = fig

        self.state.quadrants_2d = quadrants_2d

        self._build_ui()

        self.ctrl.add("on_server_ready")(self.on_server_ready)

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def state(self) -> EpiscopeState:
        return self.server.state

    @property
    def context(self):
        return self.server.context

    def on_clear_chromosome(self, quadrant_id):
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        visualization: Visualization = self.context.visualizations[quadrant_id]
        simple.HideAll(visualization.render_view)
        quadrant.chromosome = ""
        quadrant.experiment = ""
        quadrant.timestep = ""
        self.on_camera_reset(quadrant_id)

    def on_apply_chromosome(self, quadrant_id):
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        if (
            quadrant.chromosome == ""
            or quadrant.experiment == ""
            or quadrant.timestep == ""
        ):
            return

        visualization: Visualization = self.context.visualizations[quadrant_id]
        # Clear the 3D view
        simple.HideAll(visualization.render_view)
        # Clear the 2D plot
        figure: plotly_go.Figure = self.context.plot_figures[quadrant_id]
        figure.data = []

        visualization.set_chromosome(
            quadrant.chromosome, quadrant.experiment, quadrant.timestep
        )

        self.on_add_structure_display(quadrant_id, "tube", 10_000)
        self.on_add_structure_display(quadrant_id, "delaunay", -1)

        # TODO: add dynamically

        try:
            peak_track_name = next(
                iter(
                    visualization._source.get_peak_tracks(
                        quadrant.chromosome, quadrant.experiment, quadrant.timestep
                    )
                )
            )

            self.on_add_peak_track_display(quadrant_id, peak_track_name, "tube")
            self.on_add_peak_track_plot(quadrant_id, peak_track_name)
            figure.update_yaxes(title_text=peak_track_name, secondary_y=True)
        except StopIteration:
            pass

        try:
            point_track_name = next(
                iter(
                    visualization._source.get_point_tracks(
                        quadrant.chromosome, quadrant.experiment, quadrant.timestep
                    )
                )
            )

            self.on_add_point_track_display(
                quadrant_id, point_track_name, "upper_gaussian_contour"
            )
            self.on_add_point_track_display(
                quadrant_id, point_track_name, "lower_gaussian_contour"
            )
            self.on_add_point_track_plot(quadrant_id, point_track_name)
            figure.update_yaxes(title_text=point_track_name, secondary_y=False)
        except StopIteration:
            pass

        plot_widget = self.context.plot_views[quadrant_id]
        plot_widget.update(figure)

        self.on_camera_reset(quadrant_id)

    def on_add_structure_display(self, quadrant_id, representation, interpolation):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.add_structure_display(representation, interpolation)

    def on_add_peak_track_display(self, quadrant_id, track_name, representation):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.add_peak_display(track_name, representation, -1)

    def on_add_peak_track_plot(self, quadrant_id, track_name):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        figure: plotly_go.Figure = self.context.plot_figures[quadrant_id]

        point_track = visualization._source.get_peak_track(
            visualization._chromosome,
            visualization._experiment,
            visualization._timestep,
            track_name,
        )

        x = np.zeros(len(point_track) * 3)
        y = np.zeros(len(point_track) * 3)

        for i, p in enumerate(point_track):
            x[i * 3] = p["start"]
            x[i * 3 + 1] = p["summit"]
            x[i * 3 + 2] = p["end"]
            y[i * 3] = 0
            y[i * 3 + 1] = p["value"]
            y[i * 3 + 2] = 0

        figure.add_trace(plotly_go.Scatter(x=x, y=y, name=track_name), secondary_y=True)

    def on_add_point_track_display(self, quadrant_id, track_name, representation):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.add_point_display(track_name, representation, -1)

    def on_add_point_track_plot(self, quadrant_id, track_name):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        figure: plotly_go.Figure = self.context.plot_figures[quadrant_id]

        point_track = visualization._source.get_point_track(
            visualization._chromosome,
            visualization._experiment,
            visualization._timestep,
            track_name,
        )

        x = np.zeros(len(point_track))
        y = np.zeros(len(point_track))

        for i, p in enumerate(point_track):
            x[i] = p["start"]
            y[i] = p["value"]

        figure.add_trace(
            plotly_go.Scatter(x=x, y=y, name=track_name), secondary_y=False
        )

    def on_server_ready(self, *_args, **_kwargs):
        ensemble = Ensemble(self.context.data_directory)
        source = SourceProvider(ensemble)
        self.context.source = source

        chromosomes = source.get_chromosomes()
        experiments = source.get_experiments()
        timesteps = source.get_timesteps()

        self.state.chromosomes = sorted(chromosomes)
        self.state.experiments = sorted(experiments)
        self.state.timesteps = sorted(timesteps)

        for i in range(N_QUADRANTS_3D):
            render_view = self.context.render_views[i]
            visualization = Visualization(source, render_view)
            self.context.visualizations[i] = visualization

    def on_camera_reset(self, quadrant_id=None):
        quadrant_ids = range(N_QUADRANTS_3D) if quadrant_id is None else [quadrant_id]

        for i in quadrant_ids:
            pv_view = self.context.pv_views[i]
            render_view = self.context.render_views[i]
            pv_view.reset_camera()
            pv_view.update()

            simple.Render(render_view)

    def _build_ui(self):
        self.state.trame__title = "Episcope"

        with SinglePageLayout(self.server) as layout:
            self.ui = layout
            layout.title.set_text("Episcope")

            with layout.toolbar:
                pass

            with layout.content:
                with html.Div(style="width:100%; height: 100%; position: relative;"):
                    N_ROWS = N_QUADRANTS_3D // 2
                    N_COLS = N_QUADRANTS_3D // N_ROWS
                    for row in range(N_ROWS):
                        for col in range(N_COLS):
                            quadrant_id = row * 2 + col
                            with html.Div(
                                style=f"position: absolute; left: {(col / N_COLS) * 80}%; width: {(1 / N_COLS) * 80}%; width: 40%; top: {(row / N_ROWS) * 100}%; height: {(1 / N_ROWS) * 100}%; border-right-style: solid; border-bottom-style: solid; border-color: grey;"
                            ):
                                self.context.pv_views[quadrant_id] = (
                                    pv_widgets.VtkRemoteView(
                                        self.context.render_views[quadrant_id],
                                        interactive_ratio=1,
                                    )
                                )

                                quadrant: StateAdapterQuadrant3D = (
                                    self.context.quadrants_3d[quadrant_id]
                                )

                                with html.Div(
                                    style="position: absolute; top: 1rem; width: 100%;"
                                ):
                                    view_controls(
                                        quadrant,
                                        ("chromosomes",),
                                        ("experiments",),
                                        ("timesteps",),
                                        partial(self.on_clear_chromosome, quadrant_id),
                                        partial(self.on_apply_chromosome, quadrant_id),
                                        f"{quadrant.show_options_key} = !{quadrant.show_options_key}",
                                    )

                                with vuetify.VSheet(
                                    v_if=(quadrant.show_options_key, False),
                                    elevation=4,
                                    rounded=True,
                                    style="width: 26rem; position: absolute; top: 4rem; right: 2rem; padding-top: 1rem; padding-right: 1rem;",
                                ):
                                    # TODO: add dynamically
                                    representation_controls(
                                        [
                                            {"variable": "structure", "type": "tube"},
                                            {"variable": "ATAC", "type": "tube"},
                                            {
                                                "variable": "compartment",
                                                "type": "upper_gaussian_contour",
                                            },
                                            {
                                                "variable": "compartment",
                                                "type": "lower_gaussian_contour",
                                            },
                                            {
                                                "variable": "structure",
                                                "type": "delaunay",
                                            },
                                        ]
                                    )

                    with html.Div(
                        style="position: absolute; width: 20%; height: 100%; left: 80%; padding: 1rem;"
                    ):
                        for quadrant_id in range(N_QUADRANTS_2D):
                            html.H6(f"Plot {quadrant_id}", classes="text-h6")

                            with html.Div(style="height: 22%;"):
                                self.context.plot_views[quadrant_id] = plotly.Figure(
                                    self.context.plot_figures[quadrant_id]
                                )


def view_controls(
    quadrant: StateAdapterQuadrant3D,
    chromosome_options,
    experiment_options,
    timestep_options,
    clear_click,
    apply_click,
    options_click,
):
    with html.Div(style="display: flex"):
        vuetify.VSelect(
            label="Chromosome",
            v_model=(quadrant.chromosome_key,),
            variant="solo-filled",
            density="compact",
            items=chromosome_options,
            style="width: 50rem; max-width: 29%; margin-left: 1rem;",
        )
        vuetify.VSelect(
            label="Experiment",
            v_model=(quadrant.experiment_key,),
            variant="solo-filled",
            density="compact",
            items=experiment_options,
            style="width: 50rem; max-width: 29%; margin-left: 1rem;",
        )
        vuetify.VSelect(
            label="Time step",
            v_model=(quadrant.timestep_key,),
            variant="solo-filled",
            density="compact",
            items=timestep_options,
            style="width: 50rem; max-width: 29%; margin-left: 1rem;",
        )

        vuetify.VBtn(
            icon="mdi-close",
            size="small",
            density="compact",
            style="margin-left: 1rem; margin-top: 0.7rem",
            click=clear_click,
        )
        vuetify.VBtn(
            icon="mdi-check",
            size="small",
            density="compact",
            style="margin-left: 0.5rem; margin-top: 0.7rem",
            click=apply_click,
        )
        vuetify.VBtn(
            icon="mdi-cog",
            size="small",
            density="compact",
            style="margin-left: 0.5rem; margin-right: 1rem; margin-top: 0.7rem",
            click=options_click,
        )


def representation_controls(representations):
    for representation in representations:
        with html.Div(style="display: flex"):
            vuetify.VSelect(
                label="Variable",
                model_value=representation["variable"],
                variant="solo-filled",
                density="compact",
                style="max-width: 10rem; margin-left: 1rem;",
            )
            vuetify.VSelect(
                label="Representation",
                model_value=representation["type"],
                variant="solo-filled",
                density="compact",
                style="max-width: 10rem; margin-left: 1rem;",
            )
            vuetify.VBtn(
                icon="mdi-delete", density="compact", style="margin-left: 1rem;"
            )
