import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

global players 
players = []
global moves
moves = []

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
    if msg.topic == 'player_ready':
        players.append(json.loads(msg.payload))
    if '/move' in msg.topic:
        moves.append(json.loads(msg.payload))

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Lobby", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "lobby"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')
    client.subscribe(f'player_ready')
    global player_1
    global player_2
    global player_3
    global player_4
    
    client.loop_start()
    
    while(len(players) < 4): time.sleep(1)
    player_1 = players[0]['player_name']
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name': players[0]['team_name'],
                                        'player_name' : player_1}))
    player_2 = players[1]['player_name']
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':players[1]['team_name'],
                                        'player_name' : player_2}))
    
    player_3 = players[2]['player_name']
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                    'team_name': players[2]['team_name'],
                                    'player_name' : player_3}))
    
    player_4= players[3]['player_name']       
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                    'team_name': players[3]['team_name'],
                                    'player_name' : player_4}))

    time.sleep(1) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    client.subscribe(f"games/{lobby_name}/{player_1}/game_state")
    client.subscribe(f"games/{lobby_name}/{player_2}/game_state")
    client.subscribe(f"games/{lobby_name}/{player_3}/game_state")
    client.subscribe(f"games/{lobby_name}/{player_4}/game_state")
    # games/{lobby_name}/{player_name}/game_state - subscribe to it to see when the game has started and receive the following data as json (all MQTT messages comes in as a byte array) that you can retrieve using json.loads(): 
    # client.publish(f"games/{lobby_name}/start", "STOP")