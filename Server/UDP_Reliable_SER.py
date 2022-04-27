import socket
from socket import timeout
import threading
import time
from multiprocessing import Process

"""
Explaination:
This is the server side of the UDP reliable file transfer.
2 mods are used in this program:
1. Download mode -> The server will send the file to the client.
2. Upload mode -> The client will send the file to the server.

We use Go back N protocol for sending and receiving files.
we didn't implement any congestion control.
We use a buffer of 1024 bytes for each packet.

For each packet we send, we start a timer to check if the packet is lost. (we need to receive ACK)
if the packet is lost, we resend the packet and make the timer last 0.5 seconds longer.
if the timer gets to 3 seconds of waiting we stop the udp connection (Probably problem with the connection between us).

the data is sent in the following format:
code|seq|ack
and every data sent twice, code|seq|ack and than the data itself.

we compare the seq we got with the data we got and if it is the same we send ACK.

*Important*: The server is running both udp and tcp sockets at the same time. (2 threads)
"""

ReliableCode = {"ACK": '200', "SYN": '201', "SYN_ACK": '202', "Post": '203', "DIS": '204',
                "DIS_SYN": '205', "MID_PAUSE": '206', "MID_PAUSE_ACK": '207'}

class UDP_Reliable_Server:

    def __init__(self, fileport):
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.filePort = fileport # udp port for the socket
                self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket on ipv4
                self.fs.bind((self.ip, self.filePort)) # bind that socket to the ip and port

                break
            except:
                print("Couldn't bind to that port")

        self.accepted = {} # address -> User
        self.end = False

        self.init()

    def init(self):
        threading.Thread(target=self.handle_clients, args=()).start() # start thread for handling clients

    def stop(self): # stop the server
        self.end = True
        self.fs.close() # close the socket

    def kill_process(self, addr): # if we have any process running for that address (waiting for ack), kill it
        if (self.accepted[addr].process != None):
            self.accepted[addr].process.terminate()
            self.accepted[addr].process = None

    def handle_clients(self): # Main function for handling clients
        while not self.end:
            data_coded, addr = self.fs.recvfrom(1024)

            if (addr not in self.accepted):
                print(f"Receiving data from unaccepted address {addr}")
                continue

            try:
                data = data_coded.decode()
            except:
                continue

            data = data.split(sep="|", maxsplit=3) # code|seq|ack

            if(data[0] == ReliableCode["SYN"]): # client want to connect
                self.fs.sendto(ReliableCode["SYN_ACK"].encode(), addr) # send him ack for that
                print(f"Received SYN from {addr}")

                # if we on download mode we want to send the first packet
                if self.accepted[addr].mode == User.MODES["Download"]:
                    print(f"Starting to send file to {addr}")
                    if self.accepted[addr].current == len(self.accepted[addr].data): # if the file is empty
                        # the client knows the file is finished if the seq is +1 then before
                        self.accepted[addr].seq += 1
                    else:
                        # if the file isn't empty get the right seq aka the size of the next packet.
                        self.accepted[addr].seq = len(self.accepted[addr].data[self.accepted[addr].current])
                    message = "{}|{}|{}".format(ReliableCode["Post"],self.accepted[addr].seq, self.accepted[addr].ack) # post|seq|ack
                    self.accepted[addr].waiting = True # make it true, so we know we are waiting for an ack
                    self.fs.sendto(message.encode(), addr) # send the message
                    if self.accepted[addr].current != len(self.accepted[addr].data): # if the file isn't empty
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr) # send the data
                        # start a process to check if we get ack before timeout for data and the post|seq|ack
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message, self.accepted[addr].data[self.accepted[addr].current]))
                    else:
                        # start a process to check if we get ack before timeout only for post|seq|ack because file is empty
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                    self.accepted[addr].process.start() # start the process

                continue

            if(data[0] == ReliableCode["ACK"]): # client sent ack on a packet sent to him
                self.kill_process(addr) # if we have any process running for that address (waiting for ack), kill it
                self.accepted[addr].waiting = False # make it false, so we know we are not waiting for an ack

                if(self.accepted[addr].mode == User.MODES["Download"]):

                    seq = int(data[1]) # get the seq
                    ack = int(data[2]) # get the ack

                    if(ack != self.accepted[addr].seq): # if the ack is not the seq we sent than the packet got malformed
                        # send the last packet again.
                        print("Malformed packet")
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq, self.accepted[addr].ack)
                        self.fs.sendto(message.encode(), addr)
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr)
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message, self.accepted[addr].data[self.accepted[addr].current]))
                        self.accepted[addr].process.start()
                        continue

                    if(self.accepted[addr].current >= len(self.accepted[addr].data)/2 and not self.accepted[addr].mid):
                        # if we got to the middle than send a mid-pause until the client wants to continue.
                        self.accepted[addr].mid = True
                        message = ReliableCode["MID_PAUSE"]
                        self.fs.sendto(message.encode(), addr) # sending mid_pause code to client
                        # start a process to check if we get ack before timeout for mid_pause
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                        self.accepted[addr].process.start()
                        continue


                    # we get to this section if we want to send the next packet
                    self.accepted[addr].ack = seq # update the ack
                    self.accepted[addr].current += 1 # update the current (next in data array)
                    message = ""

                    send_the_data = True # will tell us if we finished the file or not

                    if (self.accepted[addr].current == len(self.accepted[addr].data)): # if we finished the file
                        self.accepted[addr].seq += 1 # then send only +1 to seq and the other side will know it ended
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq, self.accepted[addr].ack)
                        send_the_data = False # we don't want to send data only the code|seq|ack

                    else: # if we didn't finish the file
                        # we want to get the real seq to send to the client and send it with data
                        self.accepted[addr].seq += len(self.accepted[addr].data[self.accepted[addr].current])
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq,
                                                   self.accepted[addr].ack)

                    self.fs.sendto(message.encode(), addr) # send the code|seq|ack to the client
                    self.accepted[addr].waiting = True # start waiting for ack
                    if send_the_data: # if we want to send data (file is not over) send it
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr)
                        # create process for data and code|seq|ack
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message,
                                                                                           self.accepted[addr].data[self.accepted[addr].current]))
                    else:
                        # create process only for code|seq|ack
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                    self.accepted[addr].process.start() # start process


            elif(data[0] == ReliableCode["Post"]): # post mode (client upload to server)

                if(self.accepted[addr].mode != User.MODES["Upload"]): # if the mode isn't upload than something is wrong
                    continue
                print("Got Here")
                seq = int(data[1]) # get the seq
                ack = int(data[2]) # get the ack
                self.kill_process(addr) # kill the process if it exists

                if (seq - self.accepted[addr].ack == 1): # if this is the end of the file

                    self.fs.sendto(ReliableCode["DIS"].encode(), addr) # send DIS to client

                    # create a process to check if we get ack before timeout for DIS
                    self.accepted[addr].waiting = True
                    self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, ReliableCode["DIS"]))
                    self.accepted[addr].process.start()

                    # save the file on the server.
                    with open(f"./files/{self.accepted[addr].fileName}", "wb") as file:
                        for line in self.accepted[addr].data:
                            file.write(line)

                    print("Got the file successfully")
                    continue

                # if this is not the end of the file
                file_data, addr = self.fs.recvfrom(1024) # receive the next packet

                if(seq - self.accepted[addr].ack != len(file_data) or ack != self.accepted[addr].seq):
                    """ 
                    if the data got malformed - the size of the data isn't what 
                    we expected or the ack is not what we expected
                    then send client that we want the same packet again
                    """
                    code = ReliableCode["ACK"]
                    message = f"{code}|{self.accepted[addr].ack}"
                    self.fs.sendto(message.encode(), addr)
                    continue

                # if all good then we want to save that packet and send client ack on that
                self.accepted[addr].ack = seq # update the ack
                self.accepted[addr].seq += 1 # update the seq
                self.accepted[addr].data.append(file_data) # save the data

                message = "{}|{}|{}".format(ReliableCode["ACK"], self.accepted[addr].seq, self.accepted[addr].ack)
                self.fs.sendto(message.encode(), addr) # send client ack

            elif(data[0] == ReliableCode["MID_PAUSE_ACK"]): # if we got a mid-pause acknowledgement
                self.accepted[addr].pause = True # set the pause to true
                self.kill_process(addr) # kill the process if it exist

            elif(data[0] == ReliableCode["DIS"]): # client wants to disconnect
                self.kill_process(addr) # kill process if we got any

                self.accepted[addr].otherDis = True # set otherDis to true (client want to disconnect)
                self.fs.sendto(ReliableCode["DIS_SYN"].encode(), addr) # send him that we accept his disconnection

                # if we already sent him our disconnection lets just close the connection with him
                if self.accepted[addr].meDis:
                    self.kill_process(addr)
                    self.accepted.__delitem__(addr)
                    continue

                # if we didn't send him our disconnection lets send him that now
                self.fs.sendto(ReliableCode["DIS"].encode(), addr)
                self.accepted[addr].waiting = True
                self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, ReliableCode["DIS"]))
                self.accepted[addr].process.start()

            elif(data[0] == ReliableCode["DIS_SYN"]): # if he accepted our disconnection
                self.kill_process(addr)
                self.accepted[addr].waiting = False
                self.accepted[addr].meDis = True

                # if other already disconnect from us (only be happened if he disconnects first aka download mode)
                if self.accepted[addr].otherDis:
                    print("Sent the file successfully")
                    self.kill_process(addr)
                    self.accepted.__delitem__(addr)
                    continue

    def timer_to_send(self, addr, time_amount, data, message2=None):
        """
        :param time_amount: how much time to wait until resend
        :param data: what data we want to send - code|seq|ack
        :param message2: what is the actual message we want to send if we have any
        Explanation:
        This function is called with thread to deal with timeout.
        We wait for time_amount seconds and if we didn't get ACK or any indicator we want we resend the message.
        The time is increased by 0.5 sec each time until we get to 3 seconds.
        """
        time.sleep(time_amount)
        if (time_amount > 3): # if we got to 3 we have a connection problem between us, and we want to close it.
            self.accepted[addr].waiting = False
            self.accepted.__delitem__(addr)
            self.kill_process(addr)

        elif(self.accepted[addr].waiting == True):
            self.fs.sendto(data.encode(), addr)
            if(message2 != None):
                self.fs.sendto(message2, addr)
            self.timer_to_send(addr, time_amount+0.5, data)

class User: # class for each user
    MODES = {"Download":0, "Upload":1}

    def __init__(self, mode, file_name):
        self.waiting = False # if we are waiting for ack
        self.seq = 0 # seq number
        self.ack = 0 # ack number
        self.mode = mode # mode of the user (download or upload)
        self.current = 0 # current index in the file (self.data)
        self.fileName = file_name # name of the file
        self.data = [] # data of the file
        self.process = None # process of the user if there is one running (timeout process)

        # if we are downloading we want to read the file and save each part by 1024 bytes and add it to self.data
        if(mode == User.MODES["Download"]):
            with open(f"./files/{self.fileName}", "rb") as file:
                data_line = file.read(1024)
                while data_line:
                    self.data.append(data_line)
                    data_line = file.read(1024)


        self.otherDis = False # if other disconnected
        self.meDis = False # if we disconnected
        self.mid = False # if we got to mid-pause once. we will go over half of self.data more than once so we need indicator
        self.pause = False # if we are currently in mid-pause