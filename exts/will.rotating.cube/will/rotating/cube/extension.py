import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window
from .viewport_scene import ViewportSceneInfo


class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        self.viewport_scene = None
        self.widget_view_on = False
        self.ext_id = None

    def on_startup(self, ext_id):
        self.window = ui.Window("Toggle Widget View", width=300, height=300)
        self.ext_id = ext_id
        with self.window.frame:
            with ui.HStack(height=0):
                ui.Label("Toggle Widget View", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.Button("Toggle Widget", clicked_fn=self.toggle_view)

        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id, self.widget_view_on)

    def toggle_view(self):
        self.reset_viewport_scene()
        self.widget_view_on = not self.widget_view_on
        viewport_window = get_active_viewport_window()
        self.viewport_scene = ViewportSceneInfo(viewport_window, self.ext_id, self.widget_view_on)

    def reset_viewport_scene(self):
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None

    def on_shutdown(self):
        self.reset_viewport_scene()