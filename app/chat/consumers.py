from channels.generic.websocket import AsyncWebsocketConsumer
import json
import numpy as np
import cv2
import mediapipe as mp
from channels.generic.websocket import WebsocketConsumer
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import math


\
from django.shortcuts import render
from .models import *

from django.views.decorators import gzip
from django.http import StreamingHttpResponse

import threading

@gzip.gzip_page
def Home(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'app1.html')

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
class HandGestureConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.detector = HandDetector(maxHands=1)
        
        self.classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
        
        self.offset = 20
        self.imgSize = 300
        self.labels = ["A", "B", "C", "D", "E", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "F"]

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        # Convert bytes_data to numpy array (assuming it's an image)
        nparr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        hands, _ = self.detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            # Check if hand is within the expected region
            if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
                # Send None or some special value to indicate out-of-boundary
                self.send(text_data=None)
                return
            else:
                # Proceed with processing
                imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8) * 255
                imgCrop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]
                aspectRatio = h / w
                if aspectRatio > 1:
                    k = self.imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, self.imgSize))
                    wGap = math.ceil((self.imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = self.imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (self.imgSize, hCal))
                    hGap = math.ceil((self.imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize

                # Get prediction
                prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                # Send back the predicted alphabet
                self.send(text_data=self.labels[index])
        else:
            # Send None if no hands are detected
            self.send(text_data="None")

        # Check if neither bytes_data nor text_data is passed
        if bytes_data is None and text_data is None:
            print("You must pass one of bytes_data or text_data")
            pass



# class VideoStreamConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.json_file = open("model.json", "r")
#         self.model_json = self.json_file.read()
#         self.json_file.close()
#         self.model = model_from_json(self.model_json)
#         self.model.load_weights("model.h5")
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(
#             model_complexity=0,
#             min_detection_confidence=0.5,
#             min_tracking_confidence=0.5
#         )
#         self.actions = np.array(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'])
#         self.sequence = []
#         self.predictions = []
#         self.threshold = 0.8

#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data=None, bytes_data=None):
#         # Process the received frame and predict the sign
#         frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), -1)
#         cropframe = frame[40:400, 0:300]
#         image, results = self.mediapipe_detection(cropframe)

#         keypoints = self.extract_keypoints(frame,results)
#         self.sequence.append(keypoints)
#         self.sequence = self.sequence[-15:]

#         try:
#             if len(self.sequence) == 15:
#                 res = self.model.predict(np.expand_dims(self.sequence, axis=0))[0]
#                 prediction = self.actions[np.argmax(res)]
#                 print(prediction)
#                 self.predictions.append(prediction)

#                 await self.send(text_data=json.dumps({
#                     'prediction': prediction
#                 }))
#                 # if np.unique(self.predictions[-10:])[0] == np.argmax(res):
#                 #     if res[np.argmax(res)] > self.threshold:
#                 #         await self.send(text_data=json.dumps({
#                 #             'prediction': prediction
#                 #         }))
#         except Exception as e:
#             print("Error:", e)
#             pass

#     def mediapipe_detection(self, frame):
#         with self.mp_hands.Hands(
#                 static_image_mode=False,
#                 max_num_hands=2,
#                 min_detection_confidence=0.5,
#                 min_tracking_confidence=0.5) as hands:
#             results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#             return frame, results

#     def extract_keypoints(self, frame, results):
#         keypoints = []
#         if results.multi_hand_landmarks:  # Check if hands are detected
#             for res in results.multi_hand_landmarks:
#                 for id, lm in enumerate(res.landmark):
#                     h, w, c = frame.shape
#                     cx, cy = int(lm.x * w), int(lm.y * h)
#                     keypoints.append(cx)
#                     keypoints.append(cy)
#             # Ensure keypoints list has at least 63 elements
#             while len(keypoints) < 63:
#                 keypoints.extend([0, 0])  # Pad with zeros if necessary
#         else:
#             # If no hands are detected, pad the keypoints list with zeros
#             keypoints.extend([0] * 126)  # Assuming 63 keypoints with (x, y) coordinates
#         return keypoints[:63]






# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'Test-Room'

#         await self.channel_layer.group_add(
#             self.room_group_name,
            
#             self.channel_name
#         )
        
#         await self.accept()
        
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         print("Disconnected!!")
    
#     async def receive(self, text_data):
#         receive_dict = json.loads(text_data)
#         message = receive_dict['message']
#         action = receive_dict['action']
        
#         if (action == 'new-offer') or (action == 'new-answer'):
#             receiver_channel_name = receive_dict['message']['receiver_channel_name']
            
#             receive_dict['message']['receiver_channel_name'] = self.channel_name
            
#             await self.channel_layer.send(
#                 receiver_channel_name,
#                 {
#                     'type' : 'send.sdp',
#                     'receive_dict': receive_dict
#                 }
#             )
#             return
        
#         receive_dict['message']['receiver_channel_name'] = self.channel_name
        
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type' : 'send.sdp',
#                 'receive_dict': receive_dict
#             }
#         )
        
#     async def send_sdp(self, event):
#         receive_dict = event['receive_dict']
        
#         await self.send(text_data=json.dumps(receive_dict))