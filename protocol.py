import qrcode  # Library to generate QR codes
import tkinter as tk  # Tkinter library for creating GUI windows
from PIL import ImageTk  # Provides ImageTk for displaying images in Tkinter
import time  # Used for timeout control

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

def transmit_with_timeout(data, timeout=3):
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
        if check_confirmation():
            confirmation_received = True
            print("Message confirmed by receiver.")
            break
        root.update()  # Refresh the Tkinter window to keep it responsive
        time.sleep(0.1)  # Short delay between confirmation checks

    # Stop the transmission (close the Tkinter window)
    stop_transmission()

    return confirmation_received

def check_confirmation():
    """
    Placeholder function to simulate checking for a confirmation signal.
    
    Returns:
        bool: False, indicating no confirmation received.
    
    Note:
        Implement this function to add logic for checking QR code confirmation,
        e.g., by scanning a QR code using a camera.
    """

    return False  # Replace with actual confirmation check logic

# Example data to encode in the QR code
data = "fdfdfs akrfmskdfs sfsdfsd"
# Transmit the QR code with a 3-second timeout
transmit_with_timeout(data, timeout=3)
