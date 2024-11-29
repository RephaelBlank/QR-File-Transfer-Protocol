from temp1 import send_and_recv, send_and_receive_with_protocol
from concurrent.futures import ThreadPoolExecutor
from handle_file import encode_file

filepath = "C:/Users/refae/network_with_QRCode/file.txt"
msg = encode_file(filepath) 

with ThreadPoolExecutor() as executor:
        #future = executor.submit(send_and_recv, s)
        future = executor.submit(send_and_receive_with_protocol, msg)

        
        data = future.result()
        
            

        print (data)
        if data is None:
            print ("data not received")
        