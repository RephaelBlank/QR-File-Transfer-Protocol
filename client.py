from handle_file import decode_file
from temp1 import send_and_recv, handle_scan, send_and_receive_with_protocol, handle_scan_with_protocol
import queue 
import threading
from concurrent.futures import ThreadPoolExecutor



if __name__ == "__main__": 

   with ThreadPoolExecutor() as executor:
        future   = executor.submit(send_and_receive_with_protocol,str() )#msg)
        data = future.result()
        print(decode_file(data))

    
