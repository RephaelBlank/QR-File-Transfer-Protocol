from handle_file import encode_file
from temp1 import send_and_recv, send_and_receive_with_protocol
from concurrent.futures import ThreadPoolExecutor
filepath:str =r"C:\OpenAC\SadnaProjcet\ron.txt"
full_message = ["msg 1 is a very long msg more then 30 chars which should be split to different packets.","msg 2","msg 3"]
#for s in full_message:

with ThreadPoolExecutor() as executor:
    #future = executor.submit(send_and_recv, s)
    print(encode_file(filepath))
    future = executor.submit(send_and_receive_with_protocol, encode_file(filepath))
    try:
        data = future.result()
        print(data)
    except Exception as e:
        print("Error:" + str(e))

print ("end")