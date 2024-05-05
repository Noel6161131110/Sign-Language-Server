from channels.generic.websocket import AsyncWebsocketConsumer
import json
import numpy as np
import cv2
import mediapipe as mp
from channels.generic.websocket import WebsocketConsumer
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import math

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


class WordsDetectConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.detector = HandDetector(maxHands=1)
        
        self.classifier = Classifier("WordsModel/keras_model.h5", "WordsModel/labels.txt")
        
        self.offset = 20
        self.imgSize = 300
        self.labels = ["Hello", "Thanks", "I Love You", "Yes", "No", "Goodbye"]

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