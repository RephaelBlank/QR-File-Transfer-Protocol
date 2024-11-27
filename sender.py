from qrProtocol import QRProtocolSender , ProtocolState
from temp1 import send_and_recv
from concurrent.futures import ThreadPoolExecutor

def sender(): 
    qr_sender = QRProtocolSender()

    data_to_send = bytearray("This is a test message to send using QR protocol.", 'utf-8') 
    print ("data_to_send: ", data_to_send)

    qr_sender.new_data(data_to_send) 

    print("Starting QR communication protocol...")
    while True:
        packet_to_send = qr_sender.get_send_packet()
        if packet_to_send:
            print(f"Sending packet: {packet_to_send}")

        with ThreadPoolExecutor() as executor:
            future = executor.submit(send_and_recv, packet_to_send)
            data = future.result() 

        qr_sender.handle_response_state (data)
        
        if qr_sender.state == ProtocolState.TERMINATED:
            print("Protocol communication terminated.")
            break

        print(f"Current State: {qr_sender.state}")
        completed, message = qr_sender.get_message()
        if completed:
            print(f"Message received: {message}")
            break

if __name__ == "__main__": 
    sender() 