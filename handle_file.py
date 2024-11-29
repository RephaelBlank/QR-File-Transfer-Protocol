import os


# encode file to file name and binary text
def encode_file (filepath):
    filename = os.path.basename(filepath)
    with open (filepath, "rb") as file:
        file_data = file.read()
    return filename, file_data

def decode_file(messages: list, base_dir): 
    """
    Decodes messages from a queue to reconstruct a file.
    
    Parameters:
        messages (list): List containing messages (including START, filename, content, and STOP).
        base_dir (str): Base directory to save the reconstructed file.
        
    Returns:
        str: Path to the saved file.
    """
   
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
    # Initialize the list with START, filename, content, and STOP messages.
    messages = ["empty msg","START","file.txt","Message 1","Message 2","STOP","empty msg in end"]

    # Decode the file and save it to the specified directory.
    file = decode_file(messages, "C:/Users/refae/network_with_QRCode")
    print("File saved at:", file)