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

from VisualTransmissionProtocol import QRProtocolSender

def handle_scan_with_protocol (protocol_sender:QRProtocolSender,protocol_lock:threading.Lock, timeout:int = 900):
    """
    Handles scan including parsing of packets
    """
    #need a rework
    qreader = QReader()
    cap = cv2.VideoCapture(0)#start capture
    start_time = time.time()
    while time.time() - start_time < timeout:
        ret, frame = cap.read()#capture frame
        if not ret:
            break
   # Convert image color to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Read QR code from image
        decoded_text = qreader.detect_and_decode(image=rgb_frame)
        if decoded_text and  decoded_text[0]:#i.e. not none
            try:
                response =  bytearray(decoded_text[0].encode('utf-8'))
                with protocol_lock:
                    protocol_sender.handle_response_state(response)
                    if not protocol_sender.toSend and protocol_sender.receiveComplete and protocol_sender.anyDataReceive:  # nothing more to send and message was received
                        time.sleep(5)  # allow for other computer to receive STOPACK
                        break  # Stop scanning qrs
                    print ("Current state: "+ protocol_sender.state.name)
                print("Message received:"+ decoded_text[0] + " at:"+str(time.time()-start_time))

            except Exception as e:
                print(e)
                print("Error: No valid scan " +str(time.time()-start_time))

        else:
            print("Nothing detected at "+str(time.time()-start_time))
        time.sleep(0.1)#yield and allow other thread to work
    #close capture and release resources
    cap.release()
    cv2.destroyAllWindows()



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
        error_correction=qrcode.constants.ERROR_CORRECT_M# High error correction level
    )
    # Add data to the QR code
    try:
        qr.add_data(data.decode("utf-8"))
    except Exception as e:
        print(e)
        print(data)
    print("packet sent: " + data.decode("utf-8"))
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



def transmit_with_timeout_with_protocol(protocol_sender:QRProtocolSender,protocol_lock:threading.Lock  ,timeout:int=900):
    """
      Displays packets as QR codes and handles responses using the protocol.
      """
    root = tk.Tk()
    with protocol_lock:
        #protocol_sender.handle_response_state(bytearray(5))
        create_and_present_qr_with_protocol(protocol_sender.get_send_packet(),root)
    start_time = time.time()

    while time.time() - start_time < timeout:


        #generate new packet to continue communications
        with protocol_lock:
            if not protocol_sender.toSend and protocol_sender.receiveComplete and protocol_sender.anyDataReceive:#nothing more to send and message was received
                time.sleep(5)#allow for other computer to receive STOPSYNACK
                break #Stop sending qrs

            packet = protocol_sender.get_send_packet()
            if packet:
                create_and_present_qr_with_protocol(packet, root)
        root.update()
        time.sleep(0.1)

    root.destroy()


def send_and_receive_with_protocol(data:str)->str:
    """
       Creates two threads for orchestrating a send and receive communication between two computers.\n
       Uses QRProtocolSender for performing logical actions in order with the protocol
       """

    protocol_sender = QRProtocolSender()
    protocol_sender.new_data(bytearray(data.encode('utf-8')))  # Initialize the protocol with data
    protocol_sender.handle_response_state(bytearray(0))
    protocol_lock = threading.Lock()#used for ensuring that both threads dont create a race condition
    transmit_thread = threading.Thread(
        target=transmit_with_timeout_with_protocol, args=(protocol_sender ,protocol_lock)
    )

    scan_thread = threading.Thread(
        target=handle_scan_with_protocol, args=( protocol_sender ,protocol_lock)
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
            return protocol_sender.get_message()[1].decode('utf-8')





"""
if __name__ == "__main__": 

    # Example data to encode in the QR code
    data = "fdfdfs akrfmskdfs sfsdfsd"
    # Transmit the QR code with a 3-second timeout
   # result = send_and_recv(("01",data))
    result = send_and_receive_with_protocol(data)
    print("Result from handle_scan:", result)
"""