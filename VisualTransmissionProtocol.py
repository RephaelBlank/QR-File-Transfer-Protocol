from typing import  List
from enum import Enum


"""
This file describes the protocol used for qrs

sender side:
When trying to send(RTS) first packet is 'RTSSIG'
then after receiving from the other computer a 'RTSACK'
Send  'START'
then start sending data (30 chars/  bytes at a time at most)

whilst sending a packet wait for the other computer to echo it when echo is recived go to next 30 bytes packet.

When data sent is finished
Send the following bytes 0x01 + 'STOP' (converted to bytes)
wait for response "STOPACK"  from other computer
after receiving response Send following bytes "STOPSYNACK"

Data is sent as at most 30 bytes packets

Control packet is one of the packets defined at the enum ProtocolSpecialPacket


Regular packet format is as follows

bytes 0-1 used for sequence number
bytes 2-3 used for acknowledgment number
bytes 4-28 used for data
byte 29 - checksum

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
    STOP_RECIVED = "Stop received" #Send 'STOPPACK' response
    STOP_ACK_RECIEVED = "Stop Acked" # 'STOPACK' received
    TERMINATED = "Terminated" # Final state, protocol completed



class ProtocolSpecialPacket(Enum):
    """Defines the special packets in the qr protocol\n
        These packets are used for flow control and DO NOT have a sequence/acknowledge number as well as a checksum
    """
    RTS_SEND = bytearray(b'RTSSIG')
    RTS_ACK =bytearray( b'RTSACK')
    STREAM_START = bytearray(b'START')
    STREAM_STOP = bytearray(b'STOP')
    STOP_ACK =bytearray( b'STOPACK')
    STOP_ACK_SYN = bytearray(b'STOPSYNACK')



class QRProtocolSender:
    """
    This class handles the logic behind data transfer using packets as well data receiving using packet. \n
    Methods: new_data(self, data:bytearray) is used for initializing the data sending process.\n
    handle_response_state(self, response:bytearray): Run in loop for constant handling of responses(i.e new qr scans).\n
    get_send_packet(self): Returns the current packet to be shown via QR. Call it in a loop.\n
    get_message(self): Used for checking the current state of the message received from the other computer.
    """
    state:ProtocolState#Current state
    buffer_size:int#defualt buffersize
    sendBuffer:bytearray#qr data to show
    receiveBuffer:bytearray#latest received data
    packets: List[bytearray]#list of packets to send
    receiveMessage:bytearray#total message received
    toSend:bool#any data to send
    receiveComplete:bool#Complete message received
    anyDataReceive:bool#any data received
    seqnum:int#current sequence number of packet
    acknum:int#last acknowledge number of packet


    def __init__(self):
        self.buffer_size = 30  # Packet size in bytes
        self.state = ProtocolState.IDLE
        self.sendBuffer = bytearray(self.buffer_size)
        self.receiveBuffer = bytearray(self.buffer_size)
        self.packets = []
        self.toSend = False
        self.seqnum = 0
        self.acknum = -1
        self.receiveComplete = True
        self.anyDataReceive = False
        self.receiveMessage = bytearray()


    def create_packets(self, data:bytearray,):
        """
        Divides the data into packets of buffer size minus 4 (for sequencing) and saves them.
        Parameters:
            data (bytearray): The data to be sent.
        """
        self.packets =  [data[i:i + self.buffer_size-5] for i in range(0, len(data), self.buffer_size-5)]
        print (self.packets)

    def calculate_checksum(self, packet:bytearray)->bytes:
        """
        Calculate packets check sum, equals sum of all byte as unsigned chars module 256\n
        Raises ValueError if packet len isn't 29\n
        Args:
            packet:
            bytearray size of 29\n
        Returns:
        checksum byte
        """
        sum:int = 0
        if len(packet) != self.buffer_size-1:
            raise ValueError(f"Error: expected buffer len {self.buffer_size-1}, but got {len(packet)}.")
        for i in range(0,self.buffer_size-1 , 1):
            sum = (sum +packet[i])%256
        print( "length: " + str(len(sum.to_bytes(length=1,byteorder='big'))) + "val" +str(sum.to_bytes(length=1,byteorder='big')))
        return sum.to_bytes(length=1,byteorder='big')

    def new_data(self, data:bytearray):
        """
          Handles new data received and prepars the  protocol for sending.\n
          Parameters:
                  data (bytearray): The data to be sent.
          """
        if not data:#Nothing to send
            return
        self.toSend = True
        self.create_packets(data)
        self.seqnum =0
        self.acknum= -1
        self.state = ProtocolState.RTS_SEND_START
    def set_send_buffer_message(self, ack = False):
        """
        Creates a packet to send with the seqnum and acknum as the first 4bytes and 25 bytes of data and ads the checksum.\n
        Stores the packet in the send buffer.
        :return:
        """
        seqnum_bytes = self.seqnum.to_bytes(2,byteorder='big')
        try:
            acknum_bytes = self.acknum.to_bytes(2,byteorder='big')
        except Exception:#can rose when acknum is negative
            acknum_bytes = bytes(2)#compensate by putting zeros
        if ack == True:
            data_padded =  bytearray(self.buffer_size-5)

        else:
            data_padded = self.packets[self.seqnum].ljust(self.buffer_size-5, b'\x00')
        try:
            self.sendBuffer=bytearray(seqnum_bytes+acknum_bytes+data_padded+ self.calculate_checksum(bytearray(seqnum_bytes+acknum_bytes+data_padded)))
        except ValueError  :
            self.sendBuffer = bytearray([1]*30)#create illegal packet
    def parse_response_packet(self,response:bytearray,ack = False)-> tuple[int,int,bytearray,bytes]:
        """
        Parses the packet and extracts the seqnum,acknum and the message
        :param response: standard 30 byte packet
        :param ack: Marks if packet is an ack packet or not
        :return: seqnum,acknum, data,checksum
        """
        if len(response)<30:
            raise ValueError("Error: Too short packet")

        seqnum= int.from_bytes(response[0:2],byteorder='big')
        acknum= int.from_bytes(response[2:4],byteorder='big')
        if not ack:
            data = bytearray(response[4:self.buffer_size-1]).rstrip(b'\x00')
        else:
            data = bytearray(self.buffer_size-5)
        checksum = self.calculate_checksum(response[0:self.buffer_size-1])#calculate the received packet checksum
        received_checksum = int.to_bytes(response[29],length=1,byteorder='big')
        if checksum != received_checksum:#Compare calculated checksum to received packet checksum
            print("ERROR: Expected checksum: "+ checksum.decode('latin1')+ " Received checksum: " + received_checksum.decode('latin1'))
            raise ValueError("Error: Incorrect checksum")
        return seqnum,acknum,data,checksum

    def get_send_packet(self)->bytearray:
        """
        Returns the packet to be shown on the qr
        Returns:
        bytearray packet
        """
        return self.sendBuffer

    def get_message(self)->tuple[bool,bytearray]:
        """
        returns the current message received from the other computer as well as if it is complete
        Returns:
        [message completed?, current message]
        """
        return self.receiveComplete,self.receiveMessage

    def handle_response_state(self, response:bytearray):
        """
        Handles the logic control of the communication
        Updates buffers, creates packets, and receives data
        Args:
            response: Received packets


        """

        match self.state:
            case ProtocolState.IDLE:#process response and set state
                if response != ProtocolSpecialPacket.RTS_SEND.value:
                    return#Nothing to do
                else:
                    self.receiveMessage = bytearray() #empty the message buffer
                    self.receiveComplete = False
                    self.sendBuffer =bytearray(30)
                    self.state = ProtocolState.RTS_SEND_ACK#set state to indicate send ack
                return

            case ProtocolState.RTS_SEND_START:#Need to send RTSSIG so set the send buffer
                if response == ProtocolSpecialPacket.RTS_SEND.value:#Received rts from other client. yield and allow other user to send first
                    self.receiveMessage = bytearray()  # empty the message buffer
                    self.receiveComplete = False
                    self.sendBuffer = bytearray(30)
                    self.state = ProtocolState.RTS_SEND_ACK  # set state to indicate send ack
                else:#Priority is this users.
                    self.sendBuffer = ProtocolSpecialPacket.RTS_SEND.value
                    self.state= ProtocolState.RTS_SENT

                return

            case ProtocolState.RTS_SENT:  #sent RTSSIG
                if response == ProtocolSpecialPacket.RTS_ACK.value:
                    self.state = ProtocolState.RTS_ACKED

                return

            case ProtocolState.RTS_SEND_ACK:#recived a rts sig and need to send ack send
                self.sendBuffer = ProtocolSpecialPacket.RTS_ACK.value
                self.state = ProtocolState.RTS_SENT_ACK
                return

            case ProtocolState.RTS_ACKED:#recived ack
                self.state = ProtocolState.START_SEND#set state to signal send need to be sent
                self.sendBuffer =ProtocolSpecialPacket.STREAM_START.value
                return

            case ProtocolState.RTS_SENT_ACK:  # received a rts sig and sent ack
                #if response == ProtocolSpecialPacket.STREAM_START.value:  # if start received great
                self.state = ProtocolState.RECIVEING_DATA

                return

            case ProtocolState.START_SEND: #When reaching here the start was already sent and the ack was received
                self.state = ProtocolState.START_SENT
                return

            case ProtocolState.START_SENT:#Start was sent and a cycle waiting for receiving on other computer finished
                self.seqnum = 0 #init data seqnum
                self.acknum = -1#init data acknum
                self.state =ProtocolState.SENDING_DATA#signal begin sending
                return

            case ProtocolState.SENDING_DATA:#sending data
                if self.seqnum == 0 and len(response)<30:  # first packet to send and response is curruntely a non valid packet , most likely b'RTSACK'
                    self.set_send_buffer_message()
                    return
                try:
                    resseq , resack, resmessege,checksum = self.parse_response_packet(response,ack=True)#parse ack message
                except ValueError :#Illegal response length or illegal checksum
                    return
                if resack == self.seqnum:#packet was received propertly
                    self.anyDataReceive = True#signal some data was received
                    self.seqnum = self.seqnum+1#update current index packet to send
                    if self.seqnum >= len(self.packets):#all packets were sent
                        self.state = ProtocolState.DATA_SENT
                        return
                    else:#more data to send
                        self.set_send_buffer_message()
                        return
                else: #error response packet, send it again (perhaps send according to the ack num )
                    self.seqnum =resack+1
                    if self.seqnum >= len(self.packets):  # all packets were sent
                        self.state = ProtocolState.DATA_SENT
                        return
                    else:  # more data to send
                        self.set_send_buffer_message()
                        return

            case ProtocolState.RECIVEING_DATA:#Actively receiving data
                if response == ProtocolSpecialPacket.STREAM_STOP.value:#stop received
                    self.state = ProtocolState.STOP_RECIVED
                    self.sendBuffer= ProtocolSpecialPacket.STOP_ACK.value
                    return
                try:
                    resseq, resack, resmessege, checksum = self.parse_response_packet(response,ack= False)#parse data packet
                except ValueError as error:  # Illegal response length or illegal checksum
                    return
                if resseq == self.acknum+1 :#Segment received is the next expected segment
                    self.anyDataReceive = True#signal some data was received
                    self.receiveMessage= self.receiveMessage + resmessege#append to the total message
                    self.acknum = self.acknum+1
                    self.set_send_buffer_message(ack=True)
                else:#error packet
                    self.set_send_buffer_message(ack=True)#send packet with last seq received

            case ProtocolState.DATA_SENT:#all data was sent
                self.sendBuffer = ProtocolSpecialPacket.STREAM_STOP.value#Send Stop message
                if response == ProtocolSpecialPacket.STOP_ACK.value:#Stop Ack was received
                    self.state = ProtocolState.STOP_ACK_RECIEVED#update state
                    self.sendBuffer = ProtocolSpecialPacket.STOP_ACK_SYN.value#Send STOP SYNACK
                return

            case  ProtocolState.STOP_RECIVED:#Stop received
                if response == ProtocolSpecialPacket.STOP_ACK_SYN.value:# The ack message was received at the sender
                    self.state = ProtocolState.TERMINATED#receiving process is terminated
                    return
                self.sendBuffer = ProtocolSpecialPacket.STOP_ACK.value#send stop_ack
                return
            case ProtocolState.STOP_ACK_RECIEVED:#Stop ack receive
                self.sendBuffer = ProtocolSpecialPacket.STOP_ACK_SYN.value#Send syn ack
                self.state = ProtocolState.TERMINATED#end process

            case ProtocolState.TERMINATED:#Cleanup
                self.receiveBuffer = bytearray(30)
                if self.seqnum < len(self.packets):#Happens when both clients requested to send and this client has lost
                    self.toSend = True
                else:
                    self.toSend = False
                self.seqnum = 0
                self.acknum = -1

                self.receiveComplete = True
                self.state = ProtocolState.IDLE

        return

