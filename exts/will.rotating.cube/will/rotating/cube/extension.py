import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window
from .viewport_scene import ViewportSceneInfo
from .object_info_model import ObjInfoModel

class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        self.viewport_scene = None
        self.widget_view_on = False
        self.ext_id = None

    def on_startup(self, ext_id):
        self.window = ui.Window("Toggle Widget View", width=300, height=300)
        self.ext_id = ext_id
        self.model = ObjInfoModel()
        with self.window.frame:
            with ui.VStack():
                self._slider_model = ui.SimpleFloatModel()
                ui.Label("Toggle Widget View", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.Button("Toggle Widget", clicked_fn=self.toggle_view)
                ui.FloatSlider(self._slider_model)
                ui.Button("Get Position", clicked_fn=self.get_pos)
                self.pos_label = ui.Label("", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                with ui.HStack():
                    ui.Button("Left", clicked_fn=lambda: self.set_pos("LEFT"))                
                    ui.Button("Up", clicked_fn=lambda: self.set_pos("UP"))
                    ui.Button("Down", clicked_fn=lambda: self.set_pos("DOWN"))
                    ui.Button("Right", clicked_fn=lambda: self.set_pos("RIGHT"))
                self.new_pos_label = ui.Label("", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})

        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id, self.widget_view_on)

    def set_pos(self, flag):
        INCR = 20
        if self.model:
            if flag == "LEFT":
                new_coords = self.model.set_relative_position(x_incr = INCR, y_incr=0)
                self.new_pos_label.text = str(new_coords)
            elif flag == "UP":
                new_coords = self.model.set_relative_position(x_incr = 0, y_incr=-1*INCR)
                self.new_pos_label.text = str(new_coords)
            elif flag == "DOWN":
                new_coords = self.model.set_relative_position(x_incr = 0, y_incr=INCR)
                self.new_pos_label.text = str(new_coords)
            elif flag == "RIGHT":
                new_coords = self.model.set_relative_position(x_incr = -1*INCR, y_incr=0)
                self.new_pos_label.text = str(new_coords)

    def get_pos(self):
        if self.model:
            self.pos_label.text = str(self.model.get_position())
        else:
            print("fail")

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