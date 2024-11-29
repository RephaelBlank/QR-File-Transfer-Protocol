import os
import json
from queue import Queue
from qrProtocol import ProtocolSpecialPacket

# encode file to file name and binary text
def encode_file (filepath):
    filename = os.path.basename(filepath)
    with open (filepath, "rb") as file:
        file_data = file.read()
    return filename, file_data

def decode_file(queue: Queue, base_dir): 
    """
    Decodes messages from a queue to reconstruct a file.
    
    Parameters:
        queue (Queue): Queue containing messages (including START, filename, content, and STOP).
        base_dir (str): Base directory to save the reconstructed file.
        
    Returns:
        str: Path to the saved file.
    """
    # Convert queue to list.
    messages = [] 
    while not queue.empty():
        messages.append(queue.get())

    # Initialize flags and variables.
    read_data = False  # Only start reading content after START.
    filename = "error.txt"  # Default filename if none is provided.
    data_to_file = []  # List to store file content.

    # Process messages to extract filename and content.
    for msg in messages:
        print(msg)  # Debug: Print each message for verification.

        # Handle START message.
        if msg == "START": 
            read_data = True  # Begin reading data.
            continue

        # Handle STOP message.
        if msg == "STOP": 
            read_data = False  # Stop reading data.
            continue

        # If currently reading data and filename not set, set the filename.
        if read_data and filename == "error.txt":
            filename = msg  # First message after START is the filename.
            continue

        # Collect content to be written to the file.
        if read_data: 
            data_to_file.append(msg)

    # Build the file from collected content.
    file_path = os.path.join(base_dir, filename)  # Full path to save the file.
    with open(file_path, "wb") as file:
        # Write each message to the file.
        for msg in data_to_file:
            file.write(msg.encode() if isinstance(msg, str) else msg)
    
    return file_path


if __name__ == "__main__":  
    # Initialize the queue with START, filename, content, and STOP messages.
    queue = Queue()
    queue.put("empty msg")
    queue.put("START")         # Start of the file stream.
    queue.put("file.txt")      # Filename.
    queue.put("Message 1")     # First line of file content.
    queue.put("Message 2") # Second line of file content.
    queue.put("STOP")          # End of the file stream.
    queue.put("empty msg in end")

    # Decode the file and save it to the specified directory.
    file = decode_file(queue, "C:/Users/refae/network_with_QRCode")
    print("File saved at:", file)