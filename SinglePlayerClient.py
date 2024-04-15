import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

gameBegun = False
gameState = None
widerGameState = None
turnTime = False

player_name = "P1"
lobby_name = ""
team_name = "ATEAM"

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
    gameBegun, gameState, lobby_name, widerGameState, turnTime
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic_list = msg.topic.split("/")
    
    if(topic_list[-1] == "start"):
        if(msg.payload == "START"):
            gameBegun = True
            print("Game has begun")
        elif(msg.payload == "STOP"):
            gameBegun = False
            print("Game has ended")
    elif(topic_list[-1] == "game_state"):
        gameState = msg.payload
        lobby_name = topic_list[1]
        widerGameState = None
        print("board\n",msg.payload)
        turnTime = True
    elif(topic_list[0] == "teams"):
        widerGameState = {"teammateNames": gameState['teammateNames'] + msg.payload['teammateNames'] \
            , "teammatePositions": gameState['teammatePositions'] + msg.payload['teammatePositions'] \
            , "enemyPositions": gameState['enemyPositions'] + msg.payload['enemyPositions'] \
            , "currentPosition": gameState['currentPosition'] + msg.payload['currentPosition'] \
            , "coin1": gameState['coin1'] + msg.payload['coin1'] \
            , "coin2": gameState['coin2'] + msg.payload['coin2'] \
            , "coin3": gameState['coin3'] + msg.payload['coin3'] \
            , "walls": gameState['walls'] + msg.payload['walls']}
        print("board\n",msg.payload)
        turnTime = True


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
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

    player_name = "P1"#input("Enter Name")
    team_name = "ATEAM"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')
    client.subscribe(f'games/{lobby_name}/start')
    client.subscribe(f'games/{lobby_name}/stop')
    client.subscribe(f'teams/{team_name}')

    client.publish("player_ready", json.dumps({'player_name' : player_name, 'team_name' : team_name}))

    time.sleep(1) # Wait a second to resolve game start
    # client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")
    
    client.loop_start()
    # while(not gameBegun): time.sleep(1)
    while(gameBegun):
        print(f"Lobby:{lobby_name}\n")
        # while(not turnTime): time.sleep(0.1)
        client.publish(f"teams/{team_name}/{player_name}", json.dumps(gameState))
        while(widerGameState == None): time.sleep(1)
        
        
        turnTime = False
    


    
