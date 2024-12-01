from time import sleep

import qrcode  # Library to generate QR codes
import tkinter as tk  # Tkinter library for creating GUI windows
from PIL import ImageTk  # Provides ImageTk for displaying images in Tkinter
import time  # Used for timeout control
import threading

from qreader import QReader
import cv2
import time
import threading
import queue

from qrProtocol import QRProtocolSender

class TimeoutManager:
    def __init__(self, initial_timeout):
        self.timeout = initial_timeout
        self.lock = threading.Lock()

    def get_timeout(self):
        with self.lock:  
            return self.timeout

    def extend_timeout(self, extra_time):
        with self.lock:  
            self.timeout += extra_time
            print(f"Timeout extended to: {self.timeout} seconds")

    def change_timeout (self, new_time): 
        with self.lock: 
            self.timeout = new_time 
            print(f"Timeout extended to: {self.timeout} seconds")


def handle_scan (result_queue, timeout =3):
    qreader = QReader()
    cap = cv2.VideoCapture(0)
    start_time = time.time() 
    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if not ret:
            break

        # convert image color to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # read QR code from image
        decoded_text = qreader.detect_and_decode(image=rgb_frame)
        if decoded_text is not None and decoded_text !=() and decoded_text != (None,): 
                print ("dec is ", decoded_text)
                result_queue.put(decoded_text)
                cap.release()
                cv2.destroyAllWindows()
                return
        time.sleep(0.1)
    cap.release()
    cv2.destroyAllWindows()

def handle_scan_with_protocol (protocol_sender:QRProtocolSender, result_queue:queue,protocol_lock:threading.Lock,timeout_manager: TimeoutManager):
    """
    Handles scan including parsing of packets
    """
    #need a rework
    qreader = QReader()
    cap = cv2.VideoCapture(0)#start capture
    start_time = time.time()
    while time.time() - start_time < timeout_manager.get_timeout():
        ret, frame = cap.read()#capture frame
        if not ret:
            break
   # Convert image color to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Read QR code from image
        decoded_text = qreader.detect_and_decode(image=rgb_frame)
        if decoded_text and  decoded_text[0]:#i.e. not none
            try:
                response =  bytearray(decoded_text[0].encode('latin1'))
                with protocol_lock:
                    protocol_sender.handle_response_state(response)
                    print ("Current state: "+ protocol_sender.state.name)
                    timeout_manager.extend_timeout(1)
                print("Message received:"+ decoded_text[0] + " at:"+str(time.time()-start_time))
                if decoded_text[0] == "STOPACK" or decoded_text[0] == "STOPSYNACK": 
                    timeout_manager.change_timeout (0)
                result_queue.put(decoded_text[0])

            except Exception as e:
                print(e)
                print("Error: No valid scan " +str(time.time()-start_time))

        else:
            print("Nothing detected at "+str(time.time()-start_time))
        time.sleep(0.1)#yield and allow other thread to work
    #close capture and release resources
    cap.release()
    cv2.destroyAllWindows()


def create_and_present_qr(data:str):
    """
    Generates and displays a QR code in a Tkinter window.

    Parameters:
        data (str): The data to encode in the QR code.
    
    Returns:
        root (tk.Tk): The Tkinter root window displaying the QR code.
        stop_transmission (function): Function to close the Tkinter window.
    """
    # Create a QR code object with specified parameters
    qr = qrcode.QRCode(
        version=3,  # Controls the size of the QR code
        box_size=10,  # Size of each box in the QR code grid
        border=10,  # Width of the border around the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H  # High error correction level
    )
    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)  # Adjusts dimensions to fit data

    # Generate the QR code image with specified colors
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Initialize Tkinter root window
    root = tk.Tk() 
    root.title("QR Code Display")

    # Convert the QR code image for display in Tkinter
    qr_image = ImageTk.PhotoImage(img)
    label = tk.Label(root, image= qr_image)  # Place image in Tkinter label
    label.image = qr_image  # Keep a reference to the image to prevent garbage collection
    label.pack()  # Add the label to the window
    root.qr_image = qr_image  # Prevent garbage collection

    window_width = 400  # Assumed width of the QR window
    window_height = 400  # Assumed height of the QR window
    root.geometry(f"{window_width}x{window_height}+560+140")

    root.update()  # Update window to display contents immediately

    def stop_transmission():
        """Closes the Tkinter window, ending the QR code display."""
        root.destroy()

    return root, stop_transmission


def create_and_present_qr_with_protocol(data: bytearray,root:tk):
    """
    Generates and displays a QR code in a Tkinter window.

    Parameters:
        data (str): The data to encode in the QR code.

    Returns:
        root (tk.Tk): The Tkinter root window displaying the QR code.
        stop_transmission (function): Function to close the Tkinter window.
    """
    # Create a QR code object with specified parameters
    qr = qrcode.QRCode(
        version=3,  # Controls the size of the QR code
        box_size=10,  # Size of each box in the QR code grid
        border=10,  # Width of the border around the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_M  # High error correction level
    )
    # Add data to the QR code
    qr.add_data(data.decode("latin1") )
    print("packet sent: " + data.decode("latin1"))
    qr.make(fit=True)  # Adjusts dimensions to fit data

    # Generate the QR code image with specified colors
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_image = ImageTk.PhotoImage(img)#generate image

    # Initialize Tkinter root window
    root.title("QR Code Display")

    # Convert the QR code image for display in Tkinter
    window_width = 700  #width of the QR window
    window_height = 700  # height of the QR window
    root.geometry(f"{window_width}x{window_height}+560+140")#generate size
    if not hasattr(root, "qr_label"):
        qr_label = tk.Label(root, image=qr_image)#insert image
        qr_label.pack()
        root.qr_label = qr_label
    else:
        qr_label = root.qr_label
        qr_label.config(image=qr_image)
    qr_label.image = qr_image  # Prevent garbage collection and deletion of image

    root.update()  # Update window to display contents
    root.qr_image = qr_image  # Prevent garbage collection




def transmit_with_timeout(data,result_queue, timeout=6):
    """
    Displays a QR code and waits for a confirmation signal within a specified timeout.

    Parameters:
        data (str): The data to encode and display in the QR code.
        timeout (int): The duration (in seconds) to wait for a confirmation.
    
    Returns:
        bool: True if confirmation received; False if timed out.
    """
    # Initialize the QR code display and get the function to stop transmission
    root, stop_transmission = create_and_present_qr(data)
    root.mainloop()
    # Start the countdown for the transmission timeout
    start_time = time.time()
    confirmation_received = False

    # Continue displaying the QR code until timeout or confirmation
    while time.time() - start_time < timeout:
        # Check for confirmation signal
        if not result_queue.empty():
            confirmation_received = True
            print("Message confirmed by receiver.")
            break
        root.update()  # Refresh the Tkinter window to keep it responsive
        time.sleep(0.1)  # Short delay between confirmation checks

    # Stop the transmission (close the Tkinter window)
    stop_transmission()

    return confirmation_received

def transmit_with_timeout_with_protocol(protocol_sender:QRProtocolSender, result_queue,protocol_lock:threading.Lock  ,timeout_manager: TimeoutManager):
    """
      Displays packets as QR codes and handles responses using the protocol.
      """
    root = tk.Tk()
    with protocol_lock:
        #protocol_sender.handle_response_state(bytearray(5))
        create_and_present_qr_with_protocol(protocol_sender.get_send_packet(),root)
    start_time = time.time()
    confirmation_received = False

    while time.time() - start_time < timeout_manager.get_timeout():
        if not result_queue.empty():#Need care
            confirmation_received = True
            #print("Message confirmed by receiver.")


        #generate new packet to continue communications
        with protocol_lock:
            packet = protocol_sender.get_send_packet()
            if packet: 
                create_and_present_qr_with_protocol(packet, root)

        root.update()
        time.sleep(0.1)

    root.destroy()
    return confirmation_received


def send_and_recv(data):   
    result_queue = queue.Queue()
   
    transmit_thread = threading.Thread(
        target=transmit_with_timeout, args=(data, result_queue)
    )


    scan_thread = threading.Thread(target=handle_scan, args=(result_queue,))


    transmit_thread.start()
    scan_thread.start()


    transmit_thread.join()
    scan_thread.join()

    if not result_queue.empty():
        return result_queue.get() 
    return None 

def send_and_receive_with_protocol(data:str)->str:
    """
       Creates two threads for orchestrating a send and receive communication between two computers.\n
       Uses QRProtocolSender for performing logical actions in order with the protocol
       """
    received_messages = []
    timeout_manager = TimeoutManager (initial_timeout = 40)
    
    protocol_sender = QRProtocolSender()
    protocol_sender.new_data(bytearray(data.encode('latin1')))  # Initialize the protocol with data
    protocol_sender.handle_response_state(bytearray(0))
    result_queue = queue.Queue()
    protocol_lock = threading.Lock()#used for ensuring that both threads dont create a race condition
    transmit_thread = threading.Thread(
        target=transmit_with_timeout_with_protocol, args=(protocol_sender, result_queue,protocol_lock, timeout_manager)
    )

    scan_thread = threading.Thread(
        target=handle_scan_with_protocol, args=( protocol_sender, result_queue,protocol_lock, timeout_manager)
    )

    scan_thread.start()
    sleep(5)#Need to let the scan thread have a headstart since it takes much longer
    transmit_thread.start()

    try:
        transmit_thread.join()
        scan_thread.join()
    except Exception :
        return None
    with protocol_lock:
        if protocol_sender.get_message()[0]:
            print("Received message:", protocol_sender.get_message())
            received_messages.append (protocol_sender.get_message()[1])#append the message
            return protocol_sender.get_message()[1].decode('latin-1')


    return received_messages



"""
if __name__ == "__main__": 

    # Example data to encode in the QR code
    data = "fdfdfs akrfmskdfs sfsdfsd"
    # Transmit the QR code with a 3-second timeout
   # result = send_and_recv(("01",data))
    result = send_and_receive_with_protocol(data)
    print("Result from handle_scan:", result)
"""