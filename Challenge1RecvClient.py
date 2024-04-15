#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time


import paho.mqtt.client as paho
from paho import mqtt

import os
from dotenv import load_dotenv

load_dotenv("credentials.env")
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")
url = os.getenv("BROKER_ADDRESS")

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
x1 = []
x2 = []
client1 = []
client2 = []
cnt1 = 0
cnt2 = 0

# This function is called periodically from FuncAnimation
def animate(i):
    global x1, x2, client1, client2

    # Draw x and y lists
    ax.clear()
    ax.plot(x1, client1, label = "Client 1")
    ax.plot(x2, client2, label = "Client 2")

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Challenge 1')
    plt.ylabel('RANDOM MQTT BS DATA')


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)




# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("Published")
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))




# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))




# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    global x1, x2, client1, client2, cnt1, cnt2
    
    if(msg.topic == "challenge1/client1"):

        # Add x and y to lists
        x1 = range(cnt1 + 1) 
        cnt1 += 1
        client1.append(int(msg.payload))

        # Limit x and y lists to 20 items
        x1 = x1[-20:]
        client1 = client1[-20:]
    elif(msg.topic == "challenge1/client2"):

        # Add x and y to lists
        x2 = range(cnt2 + 1) 
        cnt2 += 1
        client2.append(int(msg.payload))

        # Limit x and y lists to 20 items
        x2 = x2[-20:]
        client2 = client2[-20:]




# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect


# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set(username, password)
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect(url, 8883)


# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish


# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("#", qos=1)


client.loop_start()
# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(), interval=1000)
plt.show()