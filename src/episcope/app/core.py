from __future__ import annotations

from functools import partial

import numpy as np
import plotly.graph_objects as plotly_go
import plotly.subplots as plotly_subplots
from paraview import simple
from trame.app import get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import client as client_widgets
from trame.widgets import html, plotly
from trame.widgets import paraview as pv_widgets
from trame.widgets import vuetify3 as vuetify

from episcope.app.state import Display as DisplayState
from episcope.app.state import DisplayOption, EpiscopeState, StateAdapterQuadrant3D
from episcope.library.io.v1_2 import Ensemble, SourceProvider
from episcope.library.viz.visualization import Visualization
from episcope.library.viz.selection_keys import SELECTION_OBJECT_ID, SELECTION_OBJECT_KIND

from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.vtkCommonDataModel import (
        vtkDataObject,
        vtkSelectionNode,
)
from vtkmodules.vtkCommonCore import (
        vtkIdTypeArray,
)
from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleRubberBandPick,
)
from vtkmodules.vtkRenderingCore import (
    vtkHardwareSelector,
)

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
        self.server.cli.add_argument(
            "-n",
            "--num-quadrants",
            help="Number of quadrants to display.",
            dest="num_quadrants",
            type=int,
            default=2,
        )
        self.server.cli.add_argument(
            "-o",
            "--display-options",
            help="Path to a yaml file that has overrides for the default appearance of the 3D visualization.",
            dest="display_options",
            default="",
        )
        known_args, _ = self.server.cli.parse_known_args()
        self.context.data_directory = known_args.data
        self.context.display_options = known_args.display_options

        self.N_QUADRANTS_3D = known_args.num_quadrants
        self.N_QUADRANTS_2D = self.N_QUADRANTS_3D

        self.context.reference_quadrant_id = None
        self.context.pv_views = [None] * self.N_QUADRANTS_3D
        self.context.render_views = [None] * self.N_QUADRANTS_3D
        self.context.render_window_interactors = [None] * self.N_QUADRANTS_3D
        self.context.interactor_selections = [None] * self.N_QUADRANTS_3D
        self.context.base_interactor_styles = [None] * self.N_QUADRANTS_3D
        self.context.selectors = [None] * self.N_QUADRANTS_3D
        self.context.visualizations = [None] * self.N_QUADRANTS_3D
        self.context.camera_links = [None] * self.N_QUADRANTS_3D
        self.context.vtk_selection = [False] * self.N_QUADRANTS_3D
        self.context.plot_views = [None] * self.N_QUADRANTS_2D
        self.context.plot_figures = [None] * self.N_QUADRANTS_2D
        self.context.quadrants = {}

        simple.LoadPalette(paletteName="NeutralGrayBackground")
        palette = simple.GetSettingsProxy("ColorPalette")
        palette.Background = [0.13, 0.14, 0.15]

        quadrants_3d = {}

        for i in range(self.N_QUADRANTS_3D):
            render_view = simple.CreateView("RenderView")
            render_view.SMProxy.render_window.OffScreenRenderingOn()
            quadrant = StateAdapterQuadrant3D(self.state, i)
            quadrant.chromosome = ""
            quadrant.experiment = ""
            quadrant.timestep = ""
            quadrant.displays = {}
            quadrant.display_options = {}
            quadrant.has_viz = False
            quadrant.show_options = False
            quadrants_3d[i] = quadrant
            self.context.render_views[i] = render_view
            self.context.render_window_interactors[i] = render_view.GetRenderWindow().GetInteractor()
            # maybe can use 1 for all renderviews
            self.context.interactor_selections[i] = vtkInteractorStyleRubberBandPick()
            self.context.base_interactor_styles[i] = self.context.render_window_interactors[i].GetInteractorStyle()
            self.context.selectors[i] = vtkHardwareSelector()
            self.context.selectors[i].SetRenderer(self.context.render_views[i].GetRenderer())
            self.context.selectors[i].SetFieldAssociation(vtkDataObject.FIELD_ASSOCIATION_POINTS)

        self.context.quadrants_3d = quadrants_3d

        quadrants_2d = {}

        for i in range(self.N_QUADRANTS_2D):
            fig = plotly_subplots.make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(
                title={
                    "text": f"Plot {i}",
                    "font": {"size": 14},
                    "automargin": True,
                    "yref": "container",
                },
                showlegend=False,
                # plot_bgcolor="white",
                margin={"t": 20, "l": 10, "b": 0, "r": 10},
            )
            self.context.plot_figures[i] = fig

        self.state.quadrants_2d = quadrants_2d
        self.state.link_cameras = False
        self.state.show_labels = True

        self._build_ui()

        self._install_state_dispatcher()

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

    def _realign_visualizations(self):
        reference_visualization = self.context.visualizations[
            self.context.reference_quadrant_id
        ]

        for i in range(self.N_QUADRANTS_3D):
            visualization: Visualization = self.context.visualizations[i]

            if (
                visualization._chromosome == ""
                or visualization._experiment == ""
                or visualization._timestep == ""
            ):
                continue

            visualization.align(reference_visualization)

    def on_clear_chromosome(self, quadrant_id):
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.remove_all_displays()
        self.context.pv_views[quadrant_id].update()
        quadrant.chromosome = ""
        quadrant.experiment = ""
        quadrant.timestep = ""
        visualization.set_chromosome("", "", "")
        quadrant.displays = {}
        quadrant.display_options = {}
        quadrant.has_viz = False
        quadrant.show_options = False

        if quadrant_id == self.context.reference_quadrant_id:
            self.context.reference_quadrant_id = None

        figure: plotly_go.Figure = self.context.plot_figures[quadrant_id]
        figure.data = []
        figure.update_yaxes({"title": None})
        figure.update_yaxes({"title": None}, secondary_y=True)
        plot_widget = self.context.plot_views[quadrant_id]
        plot_widget.update(figure)

    def on_remove_labels(self, quadrant_id):
        visualization: Visualization = self.context.visualizations[quadrant_id]

        labels_display_ids = []

        for display_id, display_meta in visualization._displays.items():
            if display_meta["track_type"] == "labels":
                labels_display_ids.append(display_id)

        for display_id in labels_display_ids:
            visualization.remove_display(display_id)

    def on_add_labels(self, quadrant_id):
        self.on_remove_labels(quadrant_id)

        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.add_display("labels", "labels", "labels", -1)
        visualization.add_display("labels", "labels", "spheres", -1)

    def on_apply_chromosome(self, quadrant_id):
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        quadrant.displays.clear()

        if (
            quadrant.chromosome == ""
            or quadrant.experiment == ""
            or quadrant.timestep == ""
        ):
            self.state.dirty(quadrant.displays_key)
            return

        visualization: Visualization = self.context.visualizations[quadrant_id]
        # Clear the 3D view
        visualization.remove_all_displays()
        # Clear the 2D plot
        figure: plotly_go.Figure = self.context.plot_figures[quadrant_id]
        figure.data = []

        visualization.set_chromosome(
            quadrant.chromosome, quadrant.experiment, quadrant.timestep
        )

        display_options: dict[str, DisplayOption] = {
            "structure": {
                "name": "structure",
                "type": "structure",
                "representations": ["tube", "delaunay"],
            }
        }

        for track_name in visualization._source.get_peak_tracks(
            quadrant.chromosome, quadrant.experiment, quadrant.timestep
        ):
            display_options[track_name] = {
                "name": track_name,
                "type": "peak",
                "representations": ["tube"],
            }

        for track_name in visualization._source.get_point_tracks(
            quadrant.chromosome, quadrant.experiment, quadrant.timestep
        ):
            display_options[track_name] = {
                "name": track_name,
                "type": "point",
                "representations": ["upper_gaussian_contour", "lower_gaussian_contour"],
            }

        quadrant.display_options = display_options
        quadrant.has_viz = True

        realign_all = False

        if self.context.reference_quadrant_id is None:
            self.context.reference_quadrant_id = quadrant_id
            realign_all = True
        elif self.context.reference_quadrant_id == quadrant_id:
            realign_all = True

        if realign_all:
            self._realign_visualizations()
        else:
            visualization.align(
                self.context.visualizations[self.context.reference_quadrant_id]
            )

        self.on_add_structure_display(quadrant_id, "tube", 10_000)
        self.on_add_structure_display(quadrant_id, "delaunay", -1)

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

        if self.state.show_labels:
            self.on_add_labels(quadrant_id)

        self.on_camera_reset(quadrant_id)

    def _add_display_to_state(
        self, quadrant_id, display_id, name, type, representation
    ):
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        display: DisplayState = {
            "id": display_id,
            "name": name,
            "type": type,
            "representation": {
                "name": representation,
                "parameters": {},
            },
        }
        quadrant.displays[display_id] = display
        self.state.dirty(quadrant.displays_key)

    def on_add_display_to_viz(
        self, quadrant_id, track_name, track_type, representation, interpolation
    ):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        display_id = visualization.add_display(
            track_name, track_type, representation, interpolation
        )
        self._add_display_to_state(
            quadrant_id, display_id, track_name, track_type, representation
        )

    def on_modify_display_to_viz(
        self,
        quadrant_id,
        display_id,
        track_name,
        track_type,
        representation,
        interpolation,
    ):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.modify_display(
            display_id, track_name, track_type, representation, interpolation
        )
        self._add_display_to_state(
            quadrant_id, display_id, track_name, track_type, representation
        )

    def on_add_structure_display(self, quadrant_id, representation, interpolation):
        self.on_add_display_to_viz(
            quadrant_id, "structure", "structure", representation, interpolation
        )

    def on_add_peak_track_display(self, quadrant_id, track_name, representation):
        self.on_add_display_to_viz(quadrant_id, track_name, "peak", representation, -1)

    def on_add_point_track_display(self, quadrant_id, track_name, representation):
        self.on_add_display_to_viz(quadrant_id, track_name, "point", representation, -1)

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

    def on_remove_display(self, quadrant_id, display_id):
        visualization: Visualization = self.context.visualizations[quadrant_id]
        visualization.remove_display(display_id)
        quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
        del quadrant.displays[display_id]
        self.state.dirty(quadrant.displays_key)

        self.on_camera_reset(quadrant_id, reset=False)

    def on_add_display(self, quadrant_id):
        self._add_display_to_state(
            quadrant_id, Visualization.TEMP_DISPLAY_ID, "structure", "structure", "tube"
        )

    def on_apply_display(
        self, quadrant_id, display_id, track_name, track_type, representation
    ):
        interpolation = -1
        if track_type == "structure" and representation == "tube":
            interpolation = 10_000

        if display_id == Visualization.TEMP_DISPLAY_ID:
            self.on_add_display_to_viz(
                quadrant_id, track_name, track_type, representation, interpolation
            )
            quadrant: StateAdapterQuadrant3D = self.context.quadrants_3d[quadrant_id]
            del quadrant.displays[display_id]
        else:
            self.on_modify_display_to_viz(
                quadrant_id,
                display_id,
                track_name,
                track_type,
                representation,
                interpolation,
            )

        self.on_camera_reset(quadrant_id, reset=False)

    def on_server_ready(self, *_args, **_kwargs):
        ensemble = Ensemble(self.context.data_directory, self.context.display_options)
        source = SourceProvider(ensemble)
        self.context.source = source

        chromosomes = source.get_chromosomes()
        experiments = source.get_experiments()
        timesteps = source.get_timesteps()

        self.state.chromosomes = sorted(chromosomes)
        self.state.experiments = sorted(experiments)
        self.state.timesteps = sorted(timesteps)

        for i in range(self.N_QUADRANTS_3D):
            render_view = self.context.render_views[i]
            visualization = Visualization(source, render_view)
            self.context.visualizations[i] = visualization

    def on_camera_reset(self, quadrant_id=None, reset=True):
        quadrant_ids = (
            range(self.N_QUADRANTS_3D) if quadrant_id is None else [quadrant_id]
        )

        for i in quadrant_ids:
            pv_view = self.context.pv_views[i][0]
            render_view = self.context.render_views[i]
            render_view.Update()
            if reset:
                pv_view.reset_camera()
            simple.Render(render_view)
            pv_view.update()


    def on_link_cameras(self, *_args):
        self.state.link_cameras = not self.state.link_cameras

        reference_view = self.context.render_views[0]

        if self.state.link_cameras:
            for i in range(1, self.N_QUADRANTS_3D):
                view = self.context.render_views[i]
                self.context.camera_links[i] = simple.AddCameraLink(
                    reference_view, view
                )
        else:
            for i in range(1, self.N_QUADRANTS_3D):
                if self.context.camera_links[i] is not None:
                    simple.RemoveCameraLink(self.context.camera_links[i])

    def on_toggle_labels(self, *_args):
        self.state.show_labels = not self.state.show_labels

        for quadrant_id in range(self.N_QUADRANTS_3D):
            if self.state.show_labels:
                self.on_add_labels(quadrant_id)
            else:
                self.on_remove_labels(quadrant_id)

            self.on_camera_reset(quadrant_id, False)

    # ___________INITIAL_GLOBAL_STATE_DISPATCHER_________
    def _install_state_dispatcher(self):
        state = self.server.state
        keys = [f"vtk_selection__{i}" for i in range(self.N_QUADRANTS_3D)]
        selection_prefix = "vtk_selection__"

        @state.change(*keys)
        def _sync(**kwargs):
            # kwargs only contains keys updated in that transaction
            for k, v in kwargs.items():
                if not k.startswith(selection_prefix):
                    continue

                quadrant_id = int(k[len(selection_prefix):])
                vtk_selection = bool(v)

                # mirror into your context list
                self.context.vtk_selection[quadrant_id] = vtk_selection

                # update ONLY that quadrant's interactor
                self.update_interactor(vtk_selection, quadrant_id)

    def update_interactor(self, vtk_selection, quadrant_id, **kwargs):
        if vtk_selection:
            # remote view
            self.context.render_window_interactors[quadrant_id].SetInteractorStyle(self.context.interactor_selections[quadrant_id])
            self.context.interactor_selections[quadrant_id].StartSelect()
        else:
            # remote view
            self.context.render_window_interactors[quadrant_id].SetInteractorStyle(self.context.base_interactor_styles[quadrant_id])


    # ________ON_BOX_SELECTION_CHANGE________
    def on_box_selection_change(self, selection, quadrant_id):
        global SELECTED_IDX
        selector = self.context.selectors[quadrant_id]
        area = selection.get("selection")
        selector.SetArea(
            int(area[0]),
            int(area[2]),
            int(area[1]),
            int(area[3]),
        )

        # Common server selection
        s = selector.Select()

        objects = {}
        for i in range(s.GetNumberOfNodes()):
            node = s.GetNode(i)
            props = node.GetProperties()
            prop = props.Get(vtkSelectionNode.PROP())

            object_id = None
            object_kind = None

            if prop is not None:
                keys = prop.GetPropertyKeys()
                # SELECTION_OBJECT_ID and SELECTION_OBJECT_KIND
                #   imported from selection_keys.py
                if keys is not None:
                    if keys.Has(SELECTION_OBJECT_ID):
                        object_id = keys.Get(SELECTION_OBJECT_ID)
                        objects[object_id] = i

        if 'structure-tube' not in objects.keys():
            print('Needs structure tube for selection')
        else:
            n = s.GetNode(objects['structure-tube'])
            ids = dsa.vtkDataArrayToVTKArray(n.GetSelectionData().GetArray("SelectedIds"))
            self.add_selection(quadrant_id, ids)

        # disable selection mode
        key = f"vtk_selection__{quadrant_id}"
        self.server.state[key] = False
    # ________ON_BOX_SELECTION_CHANGE________

    def add_selection(self, quadrant_id, ids=None):

        vtk_ids = vtkIdTypeArray()
        vtk_ids.SetNumberOfTuples(len(ids))
        for idx, p_id in enumerate(ids):
            vtk_ids.SetTuple1(idx, p_id)
            idx += 1

        # pass ids to renderview selection
        displays = self.context.visualizations[quadrant_id]._displays.values()
        count = 0
        for display_meta in displays:
            if display_meta["track_name"] == "select":
                select_display_id = count
                break
            else:
                count += 1
        select_display = list(displays)[count]["display"]
        select_display.ids = vtk_ids

        rep = simple.GetRepresentation(select_display.output, self.context.render_views[quadrant_id])
        if rep is None:
            rep = simple.Show(select_display.output, self.context.render_views[quadrant_id])

        for key, value in select_display.representation_properties.items():
            setattr(rep, key, value)

        self.on_camera_reset(quadrant_id, reset=False)


        # pass ids to plot

    def remove_selection(self, quadrant_id):
        print(ids)

        # pass ids to renderview selection
        # pass ids to plot

    def _build_ui(self):
        self.state.trame__title = "Episcope"

        with SinglePageLayout(self.server) as layout:
            self.ui = layout
            layout.title.set_text("Episcope")

            with layout.toolbar:
                vuetify.VBtn(
                    icon=("show_labels ? 'mdi-label' : 'mdi-label-off'",),
                    variant=("show_labels ? 'tonal' : ''",),
                    click=self.on_toggle_labels,
                )
                vuetify.VBtn(
                    icon="mdi-camera-switch",
                    variant=("link_cameras ? 'tonal' : ''",),
                    click=self.on_link_cameras,
                )

            with layout.content:
                with html.Div(style="width:100%; height: 100%; position: relative;"):
                    N_ROWS = max(self.N_QUADRANTS_3D // 2, 1)
                    N_COLS = self.N_QUADRANTS_3D // N_ROWS
                    if N_ROWS * N_COLS < self.N_QUADRANTS_3D:
                        N_COLS += 1

                    for quadrant_id in range(self.N_QUADRANTS_3D):
                        row = quadrant_id // N_COLS
                        col = quadrant_id % N_COLS

                        with html.Div(
                            style=f"position: absolute; left: {(col / N_COLS) * 80}%; width: {(1 / N_COLS) * 80}%; top: {(row / N_ROWS) * 100}%; height: {(1 / N_ROWS) * 100}%; border-right-style: solid; border-bottom-style: solid; border-color: grey;"
                        ):
                            key = f"vtk_selection__{quadrant_id}"   # unique vtk_selection per quadrant

                            self.context.pv_views[quadrant_id] = (
                                pv_widgets.VtkRemoteView(
                                    self.context.render_views[quadrant_id],
                                    interactive_ratio=1,
                                    box_selection=(key,),
                                    box_selection_change=(partial(self.on_box_selection_change, quadrant_id=quadrant_id), "[$event]"),
                                ),
                                vuetify.VCheckbox(
                                    small=True,
                                    on_icon="mdi-selection-drag",
                                    off_icon="mdi-rotate-3d",
                                    v_model=(key, False),
                                    style="color: white; position: absolute; bottom: 0; right: 0; z-index: 1;",
                                    dense=True,
                                    hide_details=True,
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
                                v_if=(
                                    f"{quadrant.show_options_key} && {quadrant.has_viz_key}",
                                ),
                                elevation=4,
                                rounded=True,
                                style="width: 35rem; position: absolute; top: 4rem; right: 2rem; padding: 1rem;",
                            ):
                                representation_controls(
                                    quadrant,
                                    partial(self.on_apply_display, quadrant_id),
                                    partial(self.on_remove_display, quadrant_id),
                                    partial(self.on_add_display, quadrant_id),
                                )

                    with html.Div(
                        style="position: absolute; width: 20%; height: 100%; left: 80%; padding: 1rem;"
                    ):
                        for quadrant_id in range(self.N_QUADRANTS_2D):
                            with html.Div(
                                style=f"height: 20rem; max-height: {(1 / self.N_QUADRANTS_2D) * 100}%;"
                            ):
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


def representation_controls(
    quadrant: StateAdapterQuadrant3D, apply_click, delete_click, add_click
):
    with client_widgets.Getter(
        name=quadrant.display_options_key, value_name="display_options"
    ):
        with client_widgets.Getter(name=quadrant.displays_key, value_name="displays"):
            with html.Div(
                v_for=("(display, display_id) of displays"), key="display_id"
            ):
                with html.Div(style="display: flex"):
                    vuetify.VSelect(
                        label="Variable",
                        model_value=("display.name",),
                        __events=[("update_model_value", "update:modelValue")],
                        update_model_value="display.name = $event; display.type = display_options[$event].type; display.representation.name = display_options[$event].representations[0];",
                        items=(
                            "Object.values(display_options).map((option) => option.name)",
                        ),
                        variant="solo-filled",
                        density="compact",
                        style="width: 15rem; margin-right: 1rem;",
                    )
                    vuetify.VSelect(
                        label="Representation",
                        v_model=("display.representation.name",),
                        items=("display_options[display.name].representations",),
                        variant="solo-filled",
                        density="compact",
                        style="width: 15rem; margin-right: 1rem;",
                    )
                    vuetify.VBtn(
                        icon="mdi-check",
                        density="compact",
                        style="margin-right: 1rem;",
                        click=(
                            apply_click,
                            "[display.id, display.name, display.type, display.representation.name]",
                        ),
                    )
                    vuetify.VBtn(
                        icon="mdi-delete",
                        density="compact",
                        style="",
                        click=(delete_click, "[display.id]"),
                    )

    vuetify.VBtn("add", block=True, compact=True, click=add_click)
