from Challenge1SendClientBase import *

client.loop_start()

while(1):
    # a single publish, this can also be done in loops, etc.
    # input()
    client.publish("challenge1/client1", payload=random.randint(0,255), qos=1)
    time.sleep(3)