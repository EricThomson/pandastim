import random
import direct.directbase.DirectStart
import time

while True:
    rand_num = random.randint(1,10)
    rand_delay = random.uniform(.5, 5)
    print(f"Messenger sending message {rand_num}")
    messenger.send("blast", [rand_num]) #messenger works b/c DirectStart
    time.sleep(rand_delay)
    





