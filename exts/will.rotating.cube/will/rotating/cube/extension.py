import omni.ext
import omni.ui as ui
from .object_info_model import ObjInfoModel
from pxr import Gf
import carb.windowing
import carb.input
import omni.appwindow

class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        self.widget_view_on = False
        self.ext_id = None

    def on_startup(self, ext_id):
        self.window = ui.Window("Toggle Widget View", width=300, height=300)
        self.ext_id = ext_id
        self.model = ObjInfoModel()
        self.step_size = 20
        self.input = None
        with self.window.frame:
            with ui.VStack():
                self._slider_model = ui.SimpleFloatModel()
                self._step_size_model = ui.SimpleIntModel()
                ui.Label("Scale Object", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.FloatSlider(self._slider_model)
                ui.Button("Get Position", clicked_fn=self.get_pos)
                self.pos_label = ui.Label("", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                with ui.HStack():
                    ui.Button("Left", clicked_fn=lambda: self.set_pos("LEFT"))                
                    ui.Button("Up", clicked_fn=lambda: self.set_pos("UP"))
                    ui.Button("Down", clicked_fn=lambda: self.set_pos("DOWN"))
                    ui.Button("Right", clicked_fn=lambda: self.set_pos("RIGHT"))
                ui.Label("Change Step Size", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.IntSlider(self._step_size_model)
                ui.Button("Start keyboard input", clicked_fn = lambda: self.start_inp())
                ui.Button("Stop keyboard input", clicked_fn = lambda: self.unsubscribe_inp())
        self.subscribe_sliders()



    def start_inp(self):
        appwindow = omni.appwindow.get_default_app_window()
        self.keyboard = appwindow.get_keyboard()
        def on_input(e):
            if e.type == carb.input.KeyboardEventType.KEY_PRESS:
                if e.input == carb.input.KeyboardInput.W or e.input == carb.input.KeyboardInput.UP:
                    self.set_pos("UP") # TODO: right now, the problem is that it deselects the current object when you press a key. change this.
                if e.input == carb.input.KeyboardInput.S or e.input == carb.input.KeyboardInput.DOWN:
                    self.set_pos("DOWN")
                if e.input == carb.input.KeyboardInput.D or e.input == carb.input.KeyboardInput.RIGHT:
                    self.set_pos("RIGHT")                
                if e.input == carb.input.KeyboardInput.A or e.input == carb.input.KeyboardInput.LEFT:
                    self.set_pos("LEFT")
            print("{} ({})".format(e.input, e.type))
            return True


        self.input = carb.input.acquire_input_interface()
        self.keyboard_sub_id = self.input.subscribe_to_keyboard_events(self.keyboard, on_input)
    
    def unsubscribe_inp(self):
        print(self.keyboard_sub_id)
        if self.input and self.keyboard:
            self.input.unsubscribe_to_keyboard_events(self.keyboard, 1) # TODO: figure out the args in this
            self.input = None


    def subscribe_sliders(self):
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")
            stage = self.model.usd_context.get_stage()
            prim = stage.GetPrimAtPath(self.model.current_path)
            scale = prim.GetAttribute("xformOp:scale") # VERY IMPORTANT: change to translate to make it translate instead of scale
            scale.Set(Gf.Vec3d(2*value, 2*value, 2*value)) # ALSO VERY IMPORTANT

        if self._slider_model:
            self._slider_subscription = None
            self._slider_model.as_float = .5
            
            # Just throw this in extension
            self._slider_subscription = self._slider_model.subscribe_value_changed_fn(
                lambda m, p=self.model.get_item("name"): update_scale(p, m.as_float)
            )

        def update_step(value):
            self.step_size = value
            
        if self._step_size_model:
            self._step_subscription = None
            self._step_size_model.as_int = 20
            
            # Just throw this in extension
            self._step_subscription = self._step_size_model.subscribe_value_changed_fn(
                lambda m: update_step(m.as_float)
            )

    def set_pos(self, flag):
        if self.model:
            if flag == "LEFT":
                self.model.set_relative_position(x_incr = self.step_size, y_incr=0)
            elif flag == "UP":
                self.model.set_relative_position(x_incr = 0, y_incr=-1*self.step_size)
            elif flag == "DOWN":
                self.model.set_relative_position(x_incr = 0, y_incr=self.step_size)
            elif flag == "RIGHT":
                self.model.set_relative_position(x_incr = -1*self.step_size, y_incr=0)

    def get_pos(self):
        if self.model:
            self.pos_label.text = str(self.model.get_position())
        else:
            print("fail")

    def on_shutdown(self):
        self._slider_subscription.unsubscribe()
        self._step_subscription.unsubscribe()
        if self.input:
            self.input = None
        self._slider_subscription = None
        self._step_subscription = None
        self.step_size = None
        pass