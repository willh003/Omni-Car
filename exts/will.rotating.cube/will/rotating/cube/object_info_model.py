from pxr import Tf
from pxr import Usd
from pxr import UsdGeom

from omni.ui_scene import scene as sc
import omni.usd
from pxr import Gf

class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """
        def __init__(self) -> None:
            super().__init__()
            self.value = [0, 0, 0]

    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None
        self.current_path = ""

        self.stage_listener = None

        self.position = ObjInfoModel.PositionItem()

        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()

            if not prim_path:
                self.current_path = ""
                self._item_changed(self.position)
                return
            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])

            if not prim.IsA(UsdGeom.Imageable):
                self.prim = None
                if self.stage_listener:
                    self.stage_listener.Revoke()
                    self.stage_listener = None
                return

            if not self.stage_listener:
                self.stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.notice_changed, stage)

            self.prim = prim
            self.current_path = prim_path[0]
            self.position.value = self.get_position()

            # Position is changed because new selected object has a different position
            self._item_changed(self.position)

    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
        elif identifier == "position":
            return self.position

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value

        return []

    def get_position(self):
        stage = self.usd_context.get_stage()
        if not stage or self.current_path == "":
            return 

        # Get position directly from USD
        prim = stage.GetPrimAtPath(self.current_path)

        loc = prim.GetAttribute("xformOp:translate") # VERY IMPORTANT: change to translate to make it translate instead of scale
        return loc.Get()

    def set_relative_position(self, x_incr, y_incr):
        stage = self.usd_context.get_stage()
        if not stage or self.current_path == "":
            return 

        # Get position directly from USD
        prim = stage.GetPrimAtPath(self.current_path)
        pos = self.get_position()

        loc = prim.GetAttribute("xformOp:translate") # VERY IMPORTANT: change to translate to make it translate instead of scale
        new_loc = [pos[0] + y_incr, pos[1], pos[2] + x_incr]
        
        loc.Set(Gf.Vec3d(new_loc[0], new_loc[1], new_loc[2])) # ALSO VERY IMPORTANT
        return new_loc

        

     # loop through all notices that get passed along until we find selected
    def notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        """Called by Tf.Notice.  Used when the current selected object changes in some way."""
        for p in notice.GetChangedInfoOnlyPaths():
            if self.current_path in str(p.GetPrimPath()):
                pass

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()