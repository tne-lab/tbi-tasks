from enum import Enum

from Events import PybEvents
from Tasks.Task import Task
from Components.Toggle import Toggle


class Raw(Task):
    """@DynamicAttrs"""
    class States(Enum):
        START_RECORD = 0
        ACTIVE = 1
        STOP_RECORD = 2

    @staticmethod
    def get_components():
        return {
            "fan": [Toggle],
            "house_light": [Toggle]
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'ephys': False,
            'record_lockout': 4,
            'duration': 10/60
        }

    def init_state(self):
        return self.States.START_RECORD

    def start(self):
        if self.ephys:
            self.log_event(PybEvents.OEEvent(self, "startRecord", {"pre": "Raw"}))

    def START_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("start_record", self.record_lockout)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "start_record":
            self.change_state(self.States.ACTIVE)

    def ACTIVE(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            self.set_timeout("raw", self.duration * 60)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "raw":
            self.change_state(self.States.STOP_RECORD)

    def STOP_RECORD(self, event: PybEvents.PybEvent):
        if isinstance(event, PybEvents.StateEnterEvent):
            if self.ephys:
                self.log_event(PybEvents.OEEvent(self, "stopRecord"))
            self.set_timeout("stop_record", self.record_lockout)
        elif isinstance(event, PybEvents.TimeoutEvent) and event.name == "stop_record":
            self.complete = True
