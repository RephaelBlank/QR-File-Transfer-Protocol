from handle_file import decode_file, select_file_folder
from QrAndCameraProtocol import   send_and_receive_with_protocol

from concurrent.futures import ThreadPoolExecutor
import os



if __name__ == "__main__": 

   with ThreadPoolExecutor() as executor:
        future   = executor.submit(send_and_receive_with_protocol,str() )#msg)
        data_rec:str = future.result()
        ok, file_name, data =  decode_file(data_rec)
        if ok:
            folder_path =  select_file_folder(file=False)#ask user for directory to save file at
            try:
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'wb') as file:
                    file.write(data)
                print("File:" + file_name + " Was saved @:" + folder_path )
            except Exception as e:
                print("ERROR: " + str(e))
        else:
            print("ERROR: Error during file data receiving")
