from enum import Enum

from Tasks.Task import Task
from Components.Toggle import Toggle
from Events.OEEvent import OEEvent


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
            self.events.append(OEEvent(self, "startRecord", {"pre": "Raw"}))

    def START_RECORD(self):
        if self.time_in_state() > self.record_lockout:
            self.change_state(self.States.ACTIVE)

    def ACTIVE(self):
        if self.time_in_state() > self.duration * 60:
            if self.ephys:
                self.events.append(OEEvent(self, "stopRecord"))
            self.change_state(self.States.STOP_RECORD)

    def is_complete(self):
        return self.state == self.States.STOP_RECORD and self.time_in_state() > self.record_lockout
