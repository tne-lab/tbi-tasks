from types import MethodType
from typing import List

from Elements.Element import Element
from GUIs.SequenceGUI import SequenceGUI

from Elements.InfoBoxElement import InfoBoxElement


class PRCSequenceGUI(SequenceGUI):

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.info_boxes = []

        def event_countup(self):
            return [str(round(task.time_elapsed() / 60, 2))]

        def trial_count_text(self):
            return [str(task.cur_trial + 1)]

        ec = InfoBoxElement(self, 372, 500, 50, 15, "SESSION TIME", 'BOTTOM', ['0'])
        ec.get_text = MethodType(event_countup, ec)
        self.info_boxes.append(ec)

        trial_count = InfoBoxElement(self, 100, 500, 50, 15, "TRIAL", "BOTTOM", ['0'])
        trial_count.get_text = MethodType(trial_count_text, trial_count)
        self.info_boxes.append(trial_count)

    def draw(self):
        super(PRCSequenceGUI, self).draw()
        for el in self.get_elements():
            el.draw()

    def get_elements(self) -> List[Element]:
        return [*self.info_boxes]