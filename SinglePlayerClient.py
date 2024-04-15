import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time, random, sys

gameBegun = False
gameState = None
widerGameState = None
turnTime = False

player_name = "P1"
lobby_name = "lobby"
team_name = "ATEAM"

allowed_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

def printGamestate(game_state):
    print("___________")
    for i in range(10):
        print("|",end="")
        for j in range(10):
            if(game_state['currentPosition'] == [i, j]):
                print("Y",end="")
            elif([i, j] == game_state['teammatePosition']):
                print("T",end="")
            elif([i, j] in game_state['teammatePositions']):
                print("T",end="")
            elif([i, j] in game_state['walls']):
                print("W",end="")
            elif([i, j] in game_state['enemyPositions']):
                print("E",end="")
            elif([i, j] in game_state['coin1']):
                print("1",end="")
            elif([i, j] in game_state['coin2']):
                print("2",end="")
            elif([i, j] in game_state['coin3']):
                print("3",end="")
            elif(i >= game_state['currentPosition'][0] - 2 and i <= game_state['currentPosition'][0] + 2 and j >= game_state['currentPosition'][1] - 2 and j <= game_state['currentPosition'][1] + 2):
                print(" ",end="")
            elif(i >= game_state['teammatePosition'][0] - 2 and i <= game_state['teammatePosition'][0] + 2 and j >= game_state['teammatePosition'][1] - 2 and j <= game_state['teammatePosition'][1] + 2):
                print(" ",end="")
            else:
                print("?",end="")
            print(" ",end="")
        print("|")
    print("-----------")

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
    global gameBegun, gameState, lobby_name, widerGameState, turnTime, player_name
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic_list = msg.topic.split("/")
    
    if(topic_list[-1] == "start"):
        print("start", str(msg.payload))
        if(str(msg.payload) == "START"):
            gameBegun = True
            print("Game has begun")
        elif(str(msg.payload) == "STOP"):
            gameBegun = False
            print("Game has ended")
    elif(topic_list[-1] == "game_state"):
        gameBegun = True
        gameState = json.loads(msg.payload)
        lobby_name = topic_list[1]
        
        widerGameState = None
        print("board\n",msg.payload)
        turnTime = True
        print("tt",turnTime)
    elif(topic_list[0] == "teams"):
        pay = json.loads(msg.payload)
        if(topic_list[-1] != player_name):
            print("Teammate GS")
            widerGameState = {"teammateNames": gameState['teammateNames'] \
                , "teammatePositions": gameState['teammatePositions'] + [pay['currentPosition']] \
                , "teammatePosition": pay['currentPosition'] \
                , "enemyPositions": gameState['enemyPositions'] +         pay['enemyPositions'] \
                , "currentPosition": gameState['currentPosition'] \
                , "coin1": gameState['coin1'] +         pay['coin1'] \
                , "coin2": gameState['coin2'] +         pay['coin2'] \
                , "coin3": gameState['coin3'] +         pay['coin3'] \
                , "walls": gameState['walls'] +         pay['walls']}
            print("wider_game_state\n", widerGameState)


if __name__ == '__main__':
    # global gameBegun, gameState, lobby_name, widerGameState, turnTime, player_name
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    
    if(sys.argv[1] == None):
        player_name = input("Enter Name")
    else:
        player_name = sys.argv[1]
    if(sys.argv[2] == None):
        team_name = input("Enter Team")
    else:
        team_name = sys.argv[2]

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player_" + player_name, userdata=None, protocol=paho.MQTTv5)
    
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
    

    client.subscribe(f"games/+/lobby")
    client.subscribe(f'games/+/{player_name}/game_state')
    client.subscribe(f'games/+/scores')
    client.subscribe(f'games/+/start')
    client.subscribe(f'games/+/stop')
    client.subscribe(f'teams/{team_name}/+')
    print('a')
    client.loop_start()

    print('b')
    client.publish("player_ready", json.dumps({'player_name' : player_name, 'team_name' : team_name}))

    # time.sleep(1) # Wait a second to resolve game start
    # client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")
    print('c')
    while(1):
        # print('d')
        if(gameBegun):
            print(f"Lobby:{lobby_name}\nPlayer:{player_name}\nTeam:{team_name}")
            while(1): 
                # print("e")
                if(turnTime):
                    print("TURN TIME")
                    client.publish(f"teams/{team_name}/{player_name}", json.dumps(gameState))
                    while(widerGameState == None): time.sleep(1)
                    printGamestate(widerGameState)

                    walls = gameState['walls']
                    closest_coin = None
                    dist = 10
                    for coin in gameState['coin1']:
                        temp = abs((gameState['currentPosition'][1]-coin[1])+ (gameState['currentPosition'][0]-coin[0]))
                        if dist>temp:
                            dist = temp
                            closest_coin = coin
                    for coin in gameState['coin2']:
                        temp = abs((gameState['currentPosition'][1]-coin[1])+ (gameState['currentPosition'][0]-coin[0]))
                        if dist>temp:
                            dist = temp
                            closest_coin = coin
                    for coin in gameState['coin3']:
                        temp = abs((gameState['currentPosition'][1]-coin[1])+ (gameState['currentPosition'][0]-coin[0]))
                        if dist>temp:
                            dist = temp
                            closest_coin = coin
                    print("closest coin is " + str(closest_coin))
        
                    if(closest_coin != None): 
                        not_moved = True
                        # if closest coin is RIGHT of current position
                        if gameState['currentPosition'][0] < closest_coin[0] and not_moved:
                            new_pos = [gameState['currentPosition'][0]+1,gameState['currentPosition'][1]]
                            if new_pos not in gameState['walls'] and new_pos not in gameState["enemyPositions"] and new_pos not in gameState["teammatePositions"]:
                                print("MOVING RIGHT")
                                client.publish(f"games/{lobby_name}/{player_name}/move", "RIGHT")
                                not_moved = False
                        # if closest coin is LEFT of current position
                        if gameState['currentPosition'][0] > closest_coin[0] and not_moved:
                            new_pos = [gameState['currentPosition'][0]-1,gameState['currentPosition'][1]]
                            if new_pos not in gameState['walls'] and new_pos not in gameState["enemyPositions"] and new_pos not in gameState["teammatePositions"]:
                                print("MOVING LEFT")
                                client.publish(f"games/{lobby_name}/{player_name}/move", "LEFT")
                                not_moved = False
                        # if closest coin is above (UP) current position
                        if (gameState['currentPosition'][1] < closest_coin[1] and not_moved):
                            new_pos = [gameState['currentPosition'][0],gameState['currentPosition'][1]+1]
                            if ((new_pos not in gameState["walls"]) and (new_pos not in gameState["enemyPositions"]) and (new_pos not in gameState["teammatePositions"])):
                                print("MOVING UP")
                                client.publish(f"games/{lobby_name}/{player_name}/move", "UP")
                                not_moved = False
                        # if closest coin is below (DOWN) of current position
                        if (gameState['currentPosition'][1] > closest_coin[1] and not_moved):
                            new_pos = [gameState['currentPosition'][0],gameState['currentPosition'][1]-1]
                            if ((new_pos not in gameState["walls"]) and (new_pos not in gameState["enemyPositions"]) and (new_pos not in gameState["teammatePositions"])):
                                print("MOVING DOWN")
                                client.publish(f"games/{lobby_name}/{player_name}/move", "DOWN")
                                not_moved = False
                    else:
                        # there is no closest coin, pick a random move
                        moves = ["RIGHT", "LEFT", "UP", "DOWN"]
                        chosen_move = moves[random.randint(0, 3)]

                        if chosen_move == 'RIGHT':
                            new_pos = [(gameState['currentPosition'][0]+1),gameState['currentPosition'][1]]
                        if chosen_move == 'LEFT':
                            new_pos = [(gameState['currentPosition'][0]-1),gameState['currentPosition'][1]]
                        if chosen_move == 'UP':
                            new_pos = [gameState['currentPosition'][0],(gameState['currentPosition'][1]+1)]
                        if chosen_move == 'DOWN':
                            new_pos = [gameState['currentPosition'][0],(gameState['currentPosition'][1]-1)]
                        if new_pos not in gameState['walls'] and new_pos not in gameState["enemyPositions"] and new_pos not in gameState["teammatePositions"] and new_pos[0]<10 and new_pos[0]>-1 and new_pos[1]<10 and new_pos>-1 :
                            print("RANDOM " + chosen_move)
                            client.publish(f"games/{lobby_name}/{player_name}/move", chosen_move)
                    #move = ""
                    #while(1):
                    #    move = input("Where do you want to move?")
                    #    if(move in allowed_moves):
                    #        break
                    #client.publish(f"games/{lobby_name}/{player_name}/move", move)
                    # exit()  
                    turnTime = False