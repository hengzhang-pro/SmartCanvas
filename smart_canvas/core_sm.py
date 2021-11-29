""" core_sm.py """

# Default packages

# External packages
import cv2
import numpy as np
from threading import Thread
import time
from pysm import State, StateMachine, Event

# Internal packages
#from smart_canvas.background import ForegroundMask
#from smart_canvas.gesture_detection import HandDetect
#from smart_canvas.filters.carousel import FilterCarousel

from background import ForegroundMask
from gesture_detection import HandDetect
from filters.carousel import FilterCarousel

class CanvasCore(object):

    def __init__(self, q_consumer):
        self.sm = self._get_state_machine()

        self.q_consumer = q_consumer
        self.frame = None
        self.stopped = False
        self.out_frame = None
        self.tick = time.time()

        self.fg_masker = ForegroundMask()
        self.hand_detector = HandDetect()
        self.filters = FilterCarousel()
        self.filtered_frame = None

        self.apply_filter_freeze_time = self.tick
        self.change_filter_freeze_time = self.tick
        self.create_background_freeze_time = self.tick + 5


    def _get_state_machine(self):

        sm = StateMachine("Core")
        start_state = StateMachine("Start")
        stop_state = State("Stop")
        proc_state = State("Process")
        apply_filter_state = State("Apply filter")
        change_filter_state = State("Change filter")
        create_background_state = State("Create background")

        sm.add_state(start_state, initial=True)
        sm.add_state(stop_state)
        start_state.add_state(proc_state, initial=True)
        start_state.add_state(apply_filter_state)
        start_state.add_state(change_filter_state)
        #start_state.add_state(create_background_state)

        start_state.add_transition(proc_state, stop_state, events="Stop", action=self.stop)

        #sm.add_transition(start_state, None, events="Start", action=self.start)
        #stop_state.add_transition(stop_state, None, events="Stop", action=self.stop)

        #start_state.add_transition(proc_state, None, events="Process", action=self.process_a, condition=self.is_running)
        start_state.add_transition(proc_state, apply_filter_state, events="Apply filter", action=self.apply_filter, condition=self.is_running)
        start_state.add_transition(proc_state, change_filter_state, events="Change filter", action=self.change_filter, condition=self.is_running)
        #start_state.add_transition(proc_state, None, events="Create background", action=self.create_background, condition=self.is_running)

        sm.initialize()
        return sm


    def is_running(self):
        return self.stopped == False

    def change_filter(self, state, event):
        print(state, event)
        print("change_filter -action function called")
        self.filters.next_filter()
        self.change_filter_freeze_time += 3

    def apply_filter(self, frame, state, event):
        print(state, event)
        print("apply_filter -action function called")
        fg_mask = self.fg_masker.apply(frame)
        masked_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
        self.filtered_frame = self.filters.current_filter(masked_frame)
        self.apply_filter_freeze_time += 5

    # Tämä on threading.py -moduulin run() metodin käynistämä alimetodi. Ei voi muokata action -metodiksi. Voisi ehdä dispatchata eventtejä.
    def process(self):
        print("processing")
        finger_count = 0
        while not self.stopped:
            self.tick = time.time()

            frame = self.q_consumer.get()

            apply_filter = (self.apply_filter_freeze_time - self.tick) > 0
            if apply_filter:
                self.out_frame = self.filtered_frame
                continue

            change_filter = (self.change_filter_freeze_time - self.tick) > 0
            if change_filter:
                cv2.putText(frame, self.filters.current_filter.__name__,
                            (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            create_background = (
                self.create_background_freeze_time - self.tick) > 0
            if create_background:
                self.fg_masker.create_background(frame)
                continue

            finger_count = self.hand_detector.count_fingers(frame)

            cv2.putText(frame, str(finger_count), (45, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.out_frame = frame

            if apply_filter or change_filter or create_background:
                continue

            if finger_count == 2:
                self.sm.dispatch(Event("Change filter"))
                #assert self.sm.leaf_state == "Change filter"
                print(self.sm.leaf_state.name)
                #self.change_filter()
                continue

            if finger_count == 5:
                self.sm.dispatch(Event("Apply filter"))
                #assert self.sm.leaf_state == "Apply filter"
                print(self.sm.leaf_state.name)
                #self.apply_filter(frame)
                continue

            self.apply_filter_freeze_time = self.tick
            self.change_filter_freeze_time = self.tick
            self.create_background_freeze_time = self.tick

    def start(self):
        print("Starting thread")
        Thread(target=self.process, args=()).start()
        print("Thread started")
        return self

    def stop(self):
        print("Stopped")
        self.stopped = True



def test():
    from render import SmartRender
    SmartRender.run()

    core = CanvasCore()
    print(core.sm.leaf_state)



if __name__ == '__main__':
    test()

