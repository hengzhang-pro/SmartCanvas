from threading import Thread
import time

import mediapipe as mp
import cv2

mpHands = mp.solutions.hands


class HandDetect:
    """
    Class that continuously gets finger count with a dedicated thread.
    """

    def __init__(self, max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8):
        self.stopped = False
        self.finger_count = 0
        self.frame = None
        self.hands = mpHands.Hands(max_num_hands=max_num_hands, min_detection_confidence=min_detection_confidence,
                                   min_tracking_confidence=min_tracking_confidence)

    def findHandLandMarks(self, image, handNumber=0, draw=False):
        originalImage = image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        landMarkList = []

        if results.multi_hand_landmarks is None:
            return landMarkList

        if results.multi_handedness:
            # label gives if hand is left or right
            label = results.multi_handedness[handNumber].classification[0].label
            # account for inversion in webcams
            if label == "Left":
                label = "Right"
            elif label == "Right":
                label = "Left"

        hand = results.multi_hand_landmarks[handNumber]
        for id, landMark in enumerate(hand.landmark):
            imgH, imgW, imgC = originalImage.shape
            xPos, yPos = int(landMark.x * imgW), int(landMark.y * imgH)
            landMarkList.append([id, xPos, yPos, label])

        return landMarkList

    def count_fingers(self, frame):
        handLandmarks = self.findHandLandMarks(image=frame, draw=False)
        count = 0
        if(len(handLandmarks) != 0):
            # Right Thumb
            if handLandmarks[4][3] == "Right" and handLandmarks[4][1] > handLandmarks[3][1]:
                count = count+1
            # Left Thumb
            elif handLandmarks[4][3] == "Left" and handLandmarks[4][1] < handLandmarks[3][1]:
                count = count+1
            if handLandmarks[8][2] < handLandmarks[6][2]:  # Index finger
                count = count+1
            if handLandmarks[12][2] < handLandmarks[10][2]:  # Middle finger
                count = count+1
            if handLandmarks[16][2] < handLandmarks[14][2]:  # Ring finger
                count = count+1
            if handLandmarks[20][2] < handLandmarks[18][2]:  # Little finger
                count = count+1
        return count

    def get_finger_count(self):
        while not self.stopped:
            time.sleep(0.5)
            if self.frame is None:
                continue
            self.finger_count = self.count_fingers(self.frame)

    def start(self):
        Thread(target=self.get_finger_count, args=()).start()
        return self

    def stop(self):
        self.stopped = True
