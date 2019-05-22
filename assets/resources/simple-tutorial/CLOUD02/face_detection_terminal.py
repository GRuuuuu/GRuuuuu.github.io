#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Harald Seipp
# Rectification(19.5.22): GRu
# 1. replace avconv to openCV
# 2. make Thread for time delay for publishing msg into IoT platform

import time
import json
import subprocess
import os
import threading

import boto3
import paho.mqtt.client as mqtt
import numpy as np
import cv2


# The callback for when a connection is established with the MQTT server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Publish message received from server")

## Set the variables for connecting to the IoT MQTT service
macAddress="000000000000" # put in the Mac address of your Laptop here
print("MAC address: " + macAddress)
topic = "iot-2/evt/status/fmt/json"
username = "use-token-auth"
password = "000000000000000000" # put in your Watson IoT service auth-token
organization = "00000" # put in your Watson IoT service org_id
deviceType = "00000" # Change to whatever you defined in Watson IoT service

## Creating the client connection
# Set clientID and broker
clientID = "d:" + organization + ":" + deviceType + ":" + macAddress
broker = organization + ".messaging.internetofthings.ibmcloud.com"
mqttc = mqtt.Client(clientID)
# Register callback functions
mqttc.on_connect = on_connect
mqttc.on_message = on_message
# Set authentication values
mqttc.username_pw_set(username, password=password)
# Don't use TLS encryption here, just show how to do it.
mqttc.connect(host=broker, port=1883, keepalive=60)
# Publishing to IBM Internet of Things Foundation
mqttc.loop_start()

## Credentials for accessing the COS service
access_key = '0000' # Put your COS access key in here
secret_key = '0000' # Put your COS secret key in here
bucket = '000000' #  Put your COS bucket name in here
s3client = boto3.resource(
  's3',
  aws_access_key_id = access_key,
  aws_secret_access_key = secret_key,
  endpoint_url = 'https://s3.us-south.cloud-object-storage.appdomain.cloud',
)

# Configure Web Cam
cap = cv2.VideoCapture(0)
cap.set(3, 640) #WIDTH
cap.set(4, 480) #HEIGHT

exitFlag=1

# publish message to IBM IoT platform every 2.5 sec
def sendM():
  msg = json.JSONEncoder().encode({"d":{"picture_name":"campic.jpg"}})
  mqttc.publish(topic, payload=msg, qos=0, retain=False)
  print ("Message published")

  if exitFlag==1:
    threading.Timer(2.5,sendM).start()
  else: print("EXIT...")

sendM()

while(True):
  # needs to be campic.jpg
  ret, frame = cap.read()
  cv2.imshow('frame',frame)
  cv2.imwrite('tmp/campic.jpg',frame)

  print ("Uploading file:")
  # to save Object Storage space
  s3client.Object(bucket, 'campic.jpg').put(Body=open('tmp/campic.jpg', 'rb'))
  
  # Cleanup at program termination (q)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exitFlag=0
    break

cap.release()
cv2.destroyAllWindows()

print ("Waiting 5 seconds for messaging to complete...")
time.sleep(5)