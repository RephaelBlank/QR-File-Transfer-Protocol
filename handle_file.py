import os
import tkinter
from tkinter import filedialog
import base64 as b64

"""
This file handles the processing and encoding of files as well as parsing and saving of data received as files
The format is as follows #filename#${filename}#data#${data} 

"""


# encode file to file name and binary text
def encode_file (filepath:str) -> str:
    filename = os.path.basename(filepath)
    with open (filepath, "rb") as file:
        file_data = file.read()
    return "#filename#"+ filename + "#data#" + b64.b64encode(file_data).decode('utf-8')


def decode_file(encoded_file:str)->tuple[bool,str,bytes]:
    if not encoded_file.startswith("#filename#") or "#data#" not in encoded_file:#data format is incorrect
        return False, str(), encoded_file.encode('utf-8')  # invalid data

    try:#try pasrsind the data correctyly
        dataparts = encoded_file.split("#data#",maxsplit=1)#split based on data seperator once, the filename cant contain # so #data# will appear for the first time as our separator
        filename = dataparts[0].replace("#filename#","",1)#replace the special mark
        data = b64.b64decode( dataparts[1].encode('utf-8'))
        return True, filename, data

    except Exception as e:
        print("Error during data parsing")
        return False, str(), encoded_file.encode('utf-8')  # invalid data



def select_file_folder(file:bool)->str:
    """
    Handles file dialog requesting user to choose a file if file arg is True or a folder otherwise
    """
    root = tkinter.Tk()#create tkinter object for file dialog
    root.withdraw()#hide window

    if file:#User should choose a file
        path = filedialog.askopenfilename(title="Select a File")
    else:#User should choose a folder
        path = filedialog.askdirectory(title="Select a Folder")

    root.destroy()
    return  path

"""
if __name__ == "__main__":
    # Initialize the list with START, filename, content, and STOP messages.
    messages = ["empty msg","START","file.txt","Message 1","Message 2","STOP","empty msg in end"]

    # Decode the file and save it to the specified directory.
    file = decode_file(messages, "C:/Users/refae/network_with_QRCode")
    print("File saved at:", file)
"""