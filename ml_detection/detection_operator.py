import bpy
from ml_detection.methods import ml_hands
from utils import log
from utils.open_cv import stream


class DetectionModalOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.feature_detection_modal"
    bl_label = "Detection Modal"

    _timer = None
    tracking_handler = None

    def execute(self, context):
        log.logger.info("RUNNING MP AS TIMER DETECTION MODAL")
        self.init_detector()
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def init_detector(self):
        self.tracking_handler = ml_hands.HandDetector()

        self.tracking_handler.stream = stream.Webcam()
        self.tracking_handler.initialize_model()
        self.tracking_handler.init_bpy_bridge()
        self.tracking_handler.set_drawing_solution()
        self.tracking_handler.listener.attach(self.tracking_handler.observer)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def modal(self, context, event):
        if event.type == "TIMER":
            rt_event = self.tracking_handler.image_detection()
            return rt_event

        if event.type in {'ESC', 'Q'}:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        del self.tracking_handler

        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        log.logger.info("CANCELLED")
        return {'CANCELLED'}
