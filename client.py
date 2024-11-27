from temp1 import send_and_recv, handle_scan, send_and_receive_with_protocol, handle_scan_with_protocol
import queue 
import threading
from concurrent.futures import ThreadPoolExecutor


#add OK to the server messages 
def confirm (data): 
    return (("OK",data[0]))

#first scan to the start of running
"""
def first_scan (): 
    result_queue = queue.Queue()

    scan_thread = threading.Thread(target=handle_scan_with_protocol(), args=(result_queue,))
    scan_thread.start()
    scan_thread.join()
    if result_queue.empty(): 
        print ("empty")
        return None
    else: 
        data = result_queue.get()
        return (data)
"""

if __name__ == "__main__": 
   # data = first_scan()

 #   while data is not None:
  #      msg = confirm (data)
   #     print (msg)
    with ThreadPoolExecutor() as executor:
        future   = executor.submit(send_and_receive_with_protocol,"" )#msg)
        data = future.result()

    
    print("No QR code detected during the scan.")
    