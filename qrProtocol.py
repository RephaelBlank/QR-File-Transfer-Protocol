import Scripts.flag
from sympy import false
from tkinter.messagebox import RETRY

from time import sleep

from enum import Enum

"""
This file describes the protocol used for qrs

sender side:
When trying to send(RTS) first packet is 'RTSSIG'
then after reciveing from the other computer a 'RTSACK'
Send  'START'
then start sending data (30 chars/  bytes at a time at most)

whilst sending a packet wait for the other computer to echo it when echo is recived go to next 30 bytes packet.

When data sent is finished
Send the following bytes 0x01 + 'STOP' (converted to bytes)
wait for response "STOPACC"  from other computer
after recivieng response Send following bytes "STOPSYNACK"

Data is sent as at most 30 bytes packets

Regular packet format is as follows

bytes 0-1 used for sequence number
bytes 2-3 used for acknowledgment number
bytes 4-29 used for data

"""
class ProtocolState(Enum):
    """Defines the states of the QR protocol."""
    IDLE = "Idle"                # Initial state, nothing happening
    RTS_SEND_START = "RTS Start Send"     # 'RTSSIG' Not  sent, send it
    RTS_SENT = "RTS Sent"     # 'RTSSIG' sent, waiting for 'RTSACK'
    RTS_SEND_ACK = "RTSSIG receive Send RTSACK"     # 'RTSSIG' recived, send 'RTSACK'
    RTS_SENT_ACK = "RTSSIG receive  RTSACK sent"     # 'RTSSIG' recived, send 'RTSACK'
    RTS_ACKED = "RTSACK recived"   # 'RTSACK' received
    START_SEND = "Send START " # send 'START'
    START_SENT = "START Sent" # 'START' sent, beginning data transmission
    SENDING_DATA = "Sending Data"  # Actively sending data packets
    RECIVEING_DATA = "Reciveing Data"  # Actively Reciveing data packets
    DATA_SENT = "Data Sent"   # All data packets sent
    STOP_SENT = "Stop Sent"   # 'STOP' signal sent
    STOP_ACKED = "Stop Acked" # 'STOPACC' received
    TERMINATED = "Terminated" # Final state, protocol completed



class ProtocolSpecialPacket(Enum):
    """Defines the special packets in the qr protocol
        This packets are used for flow control and DO NOT have a serquence/acknowledge number
    """
    RTS_SEND = b'RTSSIG'
    RTS_ACK = b'RTSACK'
    STREAM_START = b'START'
    STREAM_STOP = b'STOP'
    STOP_ACC = b'STOPACC'
    STOP_ACC_SYN = b'STOPSYNACK'


class QRProtocolSender:
    self.state:ProtocolState
    self.buffer_size:int
    self.sendBuffer:bytearray
    self.receiveBuffer:bytearray
    self.packets: List[bytearray]
    self.receiveMessege:bytearray
    self.toSend:bool
    self.seqnum:int
    self.acknum:int
    def __init__(self):
        self.buffer_size = 30  # Packet size in bytes
        self.state = ProtocolState.IDLE
        self.sendBuffer = bytearray(buffer_size)
        self.receiveBuffer = bytearray(buffer_size)
        self.packets = []
        self.toSend = False
        self.seqnum = 0
        self.acknum = -1



    def create_packets(self, data,):
        """
        Divides the data into packets of buffer size minus 4 (for sequencing) and saves them.
        Parameters:
            data (bytes): The data to be sent.
        """
        self.packets =  [data[i:i + buffer_size-4] for i in range(0, len(data), self.buffer_size-4)]


    def new_data(self, data):
        """
          Handles new data received and preprered the  protocl for sending
          Parameters:
                  data (bytes): The data to be sent.
          """
        self.toSend = True
        self.create_packets(data)
        self.seqnum =0
        self.acknum= 0
        self.state = ProtocolState.RTS_SEND_START
    def set_send_buffer_messege(self, ack = False):
        """
        Creates a packet to send with the seqnum and acknum as the first 4bytes and 26 bytes of data.
        Stores the packet in the sned buffer
        :return:
        """
        seqnum_bytes = self.seqnum.to_bytes(2,byteorder='big')
        acknum_bytes = self.acknum.to_bytes(2,byteorder='big')
        if ack== True:
            data_padded =  bytearray(26)
        else:
            data_padded = self.packets[self.seqnum].ljust(self.buffer_size-4, b'\x00')

        self.sendBuffer=bytearray(seqnum_bytes+acknum_bytes+data_padded)

    def parse_response_packet(self,response:bytearray)-> tuple[int,int,bytearray]:
        """
        Parses the packet and extracts the seqnum,acknum and the message
        :param response: standard 30 byte packet
        :return: seqnum,acknum, data
        """
        seqnum= int.from_bytes(response[0:2],byteorder='big')
        acknum= int.from_bytes(response[2:4],byteorder='big')
        data = bytearray(packet[4:]).rstrip(b'\x00')
        return seqnum,acknum,data

    def handle_response_state(self, response:bytearray):
        # add terminate handling

        match self.state:
            case ProtocolState.IDLE:#process response and set state
                if response != ProtocolSpecialPacket.RTS_SEND:
                    return#Nothing to do
                else:
                    self.state = ProtocolState.RTS_SEND_ACK#set staate to indicate send ack
                return

            case ProtocolState.RTS_SEND_START:#Need to send RTSSIG so set the send buffer
                self.sendBuffer = ProtocolSpecialPacket.RTS_SEND
                return

            case ProtocolState.RTS_SENT:  #sent RTSSIG
                if response == ProtocolSpecialPacket.RTS_ACK:
                    self.state =ProtocolState.RTS_ACKED
                else:
                    sleep(1 + random())
                return

            case ProtocolState.RTS_SEND_ACK:#recived a rts sig and need to send ack send
                self.sendBuffer = ProtocolSpecialPacket.RTS_ACK
                self.state = ProtocolState.RTS_SENT_ACK
                return

            case ProtocolState.RTS_ACKED:#recived ack
                self.state = ProtocolState.START_SEND#set state to signal send need to be sent
                return

            case ProtocolState.RTS_SENT_ACK:  # recived an rts sig and sent ack
                if response == ProtocolSpecialPacket.STREAM_START:  # if start recived great
                    self.state = ProtocolState.RECIVEING_DATA
                else:
                    sleep(1 + random())  # sleep and begin reciveing
                    self.state = ProtocolState.RECIVEING_DATA
                return

            case ProtocolState.START_SEND: #When reching here the start was already sent and the ack was recived
                self.state = ProtocolState.START_SENT
                sleep(1 + random())  # sleep and begin reciveing
                return

            case ProtocolState.START_SENT:#Start was sent and a cycle waiting for receiving on other computer finished
                self.seqnum = 0 #init data seqnum
                self.acknum = 0 #init data acknum
                self.state =ProtocolState.SENDING_DATA#signal begin sending

            case ProtocolState.SENDING_DATA:#sending data
                resseq , resack, resmessege = self.parse_response_packet(response)
                if resack == self.seqnum:#packet was recived propertly great
                    self.seqnum = self.seqnum+1#update current index packet to send
                    if resack > length(self.packets):#all packets were sent
                        self.state = ProtocolState.DATA_SENT
                        return
                    else:#more data to send
                        self.set_send_buffer_messege()
                        return
                else: #error response packet, send it again (perhaps send according to the ack num )
                    self.seqnum =resack+1
                    if self.seqnum > length(self.packets):  # all packets were sent
                        self.state = ProtocolState.DATA_SENT
                        return
                    else:  # more data to send
                        self.set_send_buffer_messege()
                        return
                    self.set_send_buffer_messege()

            case ProtocolState.RECIVEING_DATA:#Actively receivng data
                resseq, resack, resmessege = self.parse_response_packet(response)
                if resseq == self.acknum+1 :#Segment recived is the next expected segment
                    self.receiveMessege= self.receiveMessege + resmessege#append to the total messege
                    self.acknum = self.acknum+1
                    self.set_send_buffer_messege(ack=True)
                else:#error packet
                    self.set_send_buffer_messege(ack=True)#send packet with last seq recived



        return

