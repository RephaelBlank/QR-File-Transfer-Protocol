import qrcode  # Library to generate QR codes
import tkinter as tk  # Tkinter library for creating GUI windows
from PIL import ImageTk  # Provides ImageTk for displaying images in Tkinter
import time  # Used for timeout control
from flag import Flag
from qreader import QReader
import cv2
import time
import threading
import queue
    
def handle_scan (instance: Flag,result_queue, timeout =3):
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
                instance.set_value(True)
                result_queue.put(decoded_text)
                cap.release()
                cv2.destroyAllWindows()
                return
        time.sleep(0.1)
    cap.release()
    cv2.destroyAllWindows()


def create_and_present_qr(data): 
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
        box_size=20,  # Size of each box in the QR code grid
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
    label = tk.Label(root, image=qr_image)  # Place image in Tkinter label
    label.image = qr_image  # Keep a reference to the image to prevent garbage collection
    label.pack()  # Add the label to the window
    root.update()  # Update window to display contents immediately

    def stop_transmission():
        """Closes the Tkinter window, ending the QR code display."""
        root.destroy()

    return root, stop_transmission

def transmit_with_timeout(data,instance: Flag, timeout=6):
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

    # Start the countdown for the transmission timeout
    start_time = time.time()
    confirmation_received = False

    # Continue displaying the QR code until timeout or confirmation
    while time.time() - start_time < timeout:
        # Check for confirmation signal
        if instance.get_value():
            confirmation_received = True
            print("Message confirmed by receiver.")
            break
        root.update()  # Refresh the Tkinter window to keep it responsive
        time.sleep(0.1)  # Short delay between confirmation checks

    # Stop the transmission (close the Tkinter window)
    stop_transmission()

    return confirmation_received


def manager(data): 
    confirm = Flag()  
    result_queue = queue.Queue()
   
    transmit_thread = threading.Thread(
        target=transmit_with_timeout, args=(data, confirm)
    )


    scan_thread = threading.Thread(target=handle_scan, args=(confirm,result_queue))


    transmit_thread.start()
    scan_thread.start()


    transmit_thread.join()
    scan_thread.join()

    if not result_queue.empty():
        return result_queue.get() 
    return None 

# Example data to encode in the QR code
data = "fdfdfs akrfmskdfs sfsdfsd"
# Transmit the QR code with a 3-second timeout
result = manager(data)
print("Result from handle_scan:", result)
