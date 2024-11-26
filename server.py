from temp1 import send_and_recv, send_and_receive_with_protocol
from concurrent.futures import ThreadPoolExecutor

full_message = ["msg 1","msg 2","msg 3"]
for s in full_message: 
    with ThreadPoolExecutor() as executor:
        #future = executor.submit(send_and_recv, s)
        future = executor.submit(send_and_receive_with_protocol, s)
        data = future.result()
        print (data)
        if data is None:
            print ("data not received")
            break 
        if data [0] != "OK" and data [1] != s:
            print ("data not received")
            break 
print ("end")