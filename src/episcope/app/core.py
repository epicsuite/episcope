from trame.app import asynchronous, get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import html
from trame.widgets import vuetify3 as vuetify

from paraview import simple
from trame.widgets import paraview as pv_widgets
from episcope.io.directory_provider import DirectoryProvider
from episcope.io.data_source import DataSource
from episcope.io.visualization import Visualization

import plotly.graph_objects as go
from trame.widgets import plotly
import numpy as np

# fig = go.Figure(
#     data=go.Contour(
#         z=[
#             [10, 10.625, 12.5, 15.625, 20],
#             [5.625, 6.25, 8.125, 11.25, 15.625],
#             [2.5, 3.125, 5.0, 8.125, 12.5],
#             [0.625, 1.25, 3.125, 6.25, 10.625],
#             [0, 0.625, 2.5, 5.625, 10],
#         ]
#     )
# )
# fig2 = go.Figure(
#     data=go.Contour(
#         z=[
#             [5.625, 6.25, 8.125, 11.25, 15.625],
#             [2.5, 3.125, 5.0, 8.125, 12.5],
#             [10, 10.625, 12.5, 15.625, 20],
#             [0.625, 1.25, 3.125, 6.25, 10.625],
#             [0, 0.625, 2.5, 5.625, 10],
#         ]
#     )
# )

# import plotly.graph_objects as go
# import numpy as np

x = np.arange(0, 1, 0.01)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=np.sin(x * np.pi * 2)))
fig.add_trace(go.Scatter(x=x, y=np.cos(x * np.pi * 2)))
fig.update_layout(
    showlegend=False,
    # plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=x, y=np.exp(-x * 5)))
fig2.add_trace(go.Scatter(x=x, y=np.exp(-(x * x) * 5)))
fig2.update_layout(
    showlegend=False,
    # plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=x, y=x))
fig3.add_trace(go.Scatter(x=x, y=x*x))
fig3.update_layout(
    showlegend=False,
    # plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)


@TrameApp()
class App:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")

        self.context.pv_views = [None, None]
        self.context.render_views = [None, None]
        self.context.visualizations = [None, None]

        for i in range(2):
            render_view = simple.CreateView("RenderView")

            # render_view.ViewSize = [1348, 1454]
            # render_view.AxesGrid = 'Grid Axes 3D Actor'
            # render_view.CenterOfRotation = [-10.016567945480347, 7.367330193519592, 2.3772870898246765]
            # render_view.StereoType = 'Crystal Eyes'
            # render_view.CameraPosition = [-12.484265421533541, 32.05434473082866, -2.919531480745813]
            # render_view.CameraFocalPoint = [-9.973999546024272, 7.015541214401089, 2.220134705971346]
            # render_view.CameraViewUp = [0.9927010834243502, 0.08122425051033087, -0.08914695786821412]
            # render_view.CameraFocalDisk = 1.0
            # render_view.CameraParallelScale = 8.03698
            # render_view.LegendGrid = 'Legend Grid Actor'
            # render_view.PolarGrid = 'Polar Grid Actor'
            # render_view.BackEnd = 'OSPRay raycaster'
            # render_view.OSPRayMaterialLibrary = simple.GetMaterialLibrary()

            self.context.render_views[i] = render_view

        self._build_ui()

        self.ctrl.add("on_server_ready")(self.on_server_ready)

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def state(self):
        return self.server.state

    @property
    def context(self):
        return self.server.context

    def on_server_ready(self, *args, **kwargs):
        self.context.directory_provider = DirectoryProvider("/Users/alessandro.genova/work/sources/epicsuite/test_data")

        datasets = self.context.directory_provider.datasets
        timesteps = self.context.directory_provider.timesteps

        dataset_name = ["untreated", "vaccinated"]
        timestep_name = ["chr4", "chr4"]
        displays = [
            [
                {"variable": "Untr_peakcounts", "type": "tube"},
                {"variable": "Untr_Eigenvalue", "type": "upper_contour"},
                {"variable": "Untr_compartment", "type": "lower_contour"},
            ],
            # [
            #     {"variable": "Untr_peakcounts", "type": "tube"},
            #     {"variable": "Untr_Eigenvalue", "type": "upper_contour"},
            #     {"variable": "Untr_compartment", "type": "lower_contour"},
            # ],
            [
                {"variable": "Vacv_peakcounts", "type": "tube"},
                {"variable": "Vacv_Eigenvalue", "type": "upper_contour"},
                {"variable": "Vacv_compartment", "type": "lower_contour"},
            ],
        ]

        for i in range(2):
            pv_view = self.context.pv_views[i]
            render_view = self.context.render_views[i]
            # GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            visualization = Visualization(self.context.directory_provider, render_view)

            visualization.set_source(dataset_name[i], timestep_name[i])
            variables = visualization._source.variables
            variables

            for display in displays[i]:
                variable = display["variable"]
                display_type = display["type"]
                visualization.add_display(variable, display_type)

            self.context.visualizations[i] =  visualization

            # simple.Render(render_view)
            # simple.ResetCamera(render_view)
            # pv_view.reset_camera()
            # pv_view.update()
            
            simple.Render(render_view)

        self.state.datasets = datasets
        self.state.timesteps = timesteps

    def set_dataset(self, view, dataset):
        pass

    def on_camera_reset(self):
        for i in range(2):
            pv_view = self.context.pv_views[i]
            render_view = self.context.render_views[i]
            # GetInteractorStyle().SetCurrentStyleToTrackballCamera()

            # simple.Render(render_view)
            # simple.ResetCamera(render_view)
            pv_view.reset_camera()
            pv_view.update()
            
            simple.Render(render_view)

    def _build_ui(self):
        self.state.trame__title = "Episcope"

        with SinglePageLayout(self.server) as layout:
            self.ui = layout

            with layout.toolbar:
                html.Button("a", click=self.on_camera_reset)

            with layout.content:
                with html.Div(style="width:100%; height: 100%;"):
                    with html.Div(style="position: absolute; width: 40%; height: 100%; border-right-style: solid; border-right-color: grey;"):
                        self.context.pv_views[0] = pv_widgets.VtkRemoteView(
                            self.context.render_views[0],
                            interactive_ratio=1,
                        )

                        with html.Div(style="position: absolute; top: 1rem; width: 100%;"):
                            view_controls(
                                ("experiment_0", "Untreated"),
                                ("chromosome_0", "chr4"),
                                ("time_step_0", "1"),
                                "show_options_0 = !show_options_0",
                            )
                        
                        with vuetify.VSheet(
                            v_if=("show_options_0", False),
                            elevation=4, rounded=True,
                            style="width: 26rem; position: absolute; top: 4rem; right: 2rem; padding-top: 1rem; padding-right: 1rem;"
                        ):
                            representation_controls(                                [
                                {"variable": "peakcounts", "type": "tube"},
                                {"variable": "eigenvalue", "type": "upper_contour"},
                                {"variable": "compartment", "type": "lower_contour"},
                            ])

                    with html.Div(style="position: absolute; width: 40%; height: 100%; left: 40%; border-right-style: solid; border-right-color: grey;"):
                        self.context.pv_views[1] = pv_widgets.VtkRemoteView(
                            self.context.render_views[1],
                            interactive_ratio=1,
                        )

                        with html.Div(style="position: absolute; top: 1rem; width: 100%;"):
                            view_controls(
                                ("experiment_1", "Vaccinated"),
                                ("chromosome_1", "chr4"),
                                ("time_step_1", "1"),
                                "show_options_1 = !show_options_1",
                            )
                        
                        with vuetify.VSheet(
                            v_if=("show_options_1", False),
                            elevation=4, rounded=True,
                            style="width: 26rem; position: absolute; top: 4rem; right: 2rem; padding-top: 1rem; padding-right: 1rem;"
                        ):
                            representation_controls(                                [
                                {"variable": "peakcounts", "type": "tube"},
                                {"variable": "eigenvalue", "type": "upper_contour"},
                                {"variable": "compartment", "type": "lower_contour"},
                            ])

                    with html.Div(style="position: absolute; width: 20%; height: 100%; left: 80%; padding: 1rem;"):
                        html.H6("Plot 1", classes="text-h6")

                        with html.Div(style="height: 20rem;"):
                            plotly.Figure(fig)

                        html.H6("Plot 2", classes="text-h6")

                        with html.Div(style="height: 20rem;"):
                            plotly.Figure(fig2)

                        html.H6("Plot 3", classes="text-h6")

                        with html.Div(style="height: 20rem;"):
                            plotly.Figure(fig3)

def view_controls(experiment, chromosome, time_step, options_click):
    with html.Div(style="display: flex"):
        vuetify.VSelect(
            label="Experiment", v_model=experiment, variant="solo-filled", density="compact",
            style="width: 50rem; max-width: 29%; margin-left: 1rem;"
        )
        vuetify.VSelect(
            label="Chromosome", v_model=chromosome, variant="solo-filled", density="compact",
            style="width: 50rem; max-width: 29%; margin-left: 1rem;"
        )
        vuetify.VSelect(
            label="Time step", v_model=time_step, variant="solo-filled", density="compact",
            style="width: 50rem; max-width: 29%; margin-left: 1rem;"
        )

        vuetify.VBtn(icon="mdi-cog", density="compact", style="margin-left: 1rem;", click=options_click)

def representation_controls(representations):
    for representation in representations:
        with html.Div(style="display: flex"):
            vuetify.VSelect(
                label="Variable", model_value=representation["variable"], variant="solo-filled", density="compact",
                style="max-width: 10rem; margin-left: 1rem;"
            )
            vuetify.VSelect(
                label="Representation", model_value=representation["type"], variant="solo-filled", density="compact",
                style="max-width: 10rem; margin-left: 1rem;"
            )
            vuetify.VBtn(icon="mdi-delete", density="compact", style="margin-left: 1rem;")