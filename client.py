from temp1 import send_and_recv,handle_scan
import queue 
import threading

#add OK to the server messages 
def confirm (data): 
    return (("OK",data[0]))

#first scan to the start of running 
def first_scan (): 
    result_queue = queue.Queue()

    scan_thread = threading.Thread(target=handle_scan, args=(result_queue,))
    scan_thread.start()
    scan_thread.join()
    if result_queue.empty(): 
        print ("empty")
        return None
    else: 
        data = result_queue.get()
        return (data)
    

if __name__ == "__main__": 
    data = first_scan()
    print ("exit:", data)

    while data is not None:
        msg = confirm (data)
        print (msg)
        data = send_and_recv(msg)
    
    print("No QR code detected during the scan.")
    