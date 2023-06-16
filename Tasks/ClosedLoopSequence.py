from enum import Enum

from Events import PybEvents
from Tasks.TaskSequence import TaskSequence
from ..Tasks.Raw import Raw
from ..Tasks.ERP import ERP
from ..Tasks.ClosedLoop import ClosedLoop


class ClosedLoopSequence(TaskSequence):
    """@DynamicAttrs"""
    class States(Enum):
        PRE_RAW = 0
        PRE_ERP = 1
        CLOSED_LOOP = 2
        POST_ERP = 3
        POST_RAW_RECORD = 4
        POST_RAW_NORECORD = 5

    @staticmethod
    def get_tasks():
        return [Raw, ERP, ClosedLoop]

    # noinspection PyMethodMayBeStatic
    def get_variables(self):
        return {
            'raw_num': 1
        }

    # noinspection PyMethodMayBeStatic
    def get_constants(self):
        return {
            'pre_raw_protocol': None,
            'pre_erp_protocol': None,
            'closed_loop_protocol': None,
            'post_erp_protocol': None,
            'post_raw_record_protocol': None,
            'post_raw_norecord_protocol': None,
            'post_recordings': 6
        }

    def start(self):
        self.fan.toggle(True)
        self.house_light.toggle(True)

    def stop(self):
        self.fan.toggle(False)
        self.house_light.toggle(False)

    def init_state(self):
        return self.States.PRE_RAW

    def PRE_RAW(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.StateEnterEvent) and event.task is self:
            self.switch_task(Raw, self.pre_raw_protocol)
            return True
        elif isinstance(event, PybEvents.TaskCompleteEvent):
            self.switch_task(ERP, self.pre_erp_protocol, new_state=self.States.PRE_ERP)
            return True

    def PRE_ERP(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TaskCompleteEvent):
            self.switch_task(ClosedLoop, self.closed_loop_protocol, new_state=self.States.CLOSED_LOOP)
            return True

    def CLOSED_LOOP(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TaskCompleteEvent):
            self.switch_task(ERP, self.post_erp_protocol, new_state=self.States.POST_ERP)
            return True

    def POST_ERP(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TaskCompleteEvent):
            self.switch_task(Raw, self.post_raw_record_protocol, new_state=self.States.POST_RAW_RECORD)
            return True

    def POST_RAW_RECORD(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TaskCompleteEvent):
            if self.raw_num == self.post_recordings:
                self.complete = True
            else:
                self.switch_task(Raw, self.post_raw_norecord_protocol, new_state=self.States.POST_RAW_NORECORD)
            return True

    def POST_RAW_NORECORD(self, event: PybEvents.PybEvent) -> bool:
        if isinstance(event, PybEvents.TaskCompleteEvent):
            self.switch_task(Raw, self.post_raw_record_protocol, new_state=self.States.POST_RAW_RECORD)
            self.raw_num += 1
            return True
