from enum import Enum

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
            'post_recordings': 6,
            'do_erps': True
        }

    def start(self):
        self.fan.toggle(True)
        self.house_light.toggle(True)

    def stop(self):
        self.fan.toggle(False)
        self.house_light.toggle(False)

    def init_state(self):
        return self.States.PRE_RAW

    def init_sequence(self):
        return Raw, self.pre_raw_protocol

    def PRE_RAW(self):
        if self.cur_task.is_complete():
            if self.do_erps:
                self.switch_task(ERP, self.States.PRE_ERP, self.pre_erp_protocol)
            else:
                self.switch_task(ClosedLoop, self.States.CLOSED_LOOP, self.closed_loop_protocol)

    def PRE_ERP(self):
        if self.cur_task.is_complete():
            self.switch_task(ClosedLoop, self.States.CLOSED_LOOP, self.closed_loop_protocol)

    def CLOSED_LOOP(self):
        if self.cur_task.is_complete():
            if self.do_erps:
                self.switch_task(ERP, self.States.POST_ERP, self.post_erp_protocol)
            else:
                self.switch_task(Raw, self.States.POST_RAW_RECORD, self.post_raw_record_protocol)

    def POST_ERP(self):
        if self.cur_task.is_complete():
            self.switch_task(Raw, self.States.POST_RAW_RECORD, self.post_raw_record_protocol)

    def POST_RAW_RECORD(self):
        if self.cur_task.is_complete():
            self.switch_task(Raw, self.States.POST_RAW_NORECORD, self.post_raw_norecord_protocol)

    def POST_RAW_NORECORD(self):
        if self.cur_task.is_complete() and self.raw_num < self.post_recordings:
            self.switch_task(Raw, self.States.POST_RAW_RECORD, self.post_raw_record_protocol)
            self.raw_num += 1

    def is_complete(self):
        return self.state == self.States.POST_RAW_NORECORD and self.cur_task.is_complete() and self.raw_num == self.post_recordings
