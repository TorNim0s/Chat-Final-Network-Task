import socket
import threading
import time

ReliableCode = {"ACK": '200', "SYN": '201', "SYN_ACK": '202', "Post": '203', "DIS": '204',
                "DIS_SYN": '205', "MID_PAUSE": '206', "MID_PAUSE_ACK": '207'}

ReadSize = 1000 # read 1000 bytes from file each time
MODES = {"Download": 0, "Upload": 1}

class UDP_Reliable_Client:
    def __init__(self, serverip, serverport, notification_fucntion):
        self.notification_function = notification_fucntion # fuction to update gui
        self.serverip = serverip
        self.serverport = serverport
        try:
            self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
            self.fs.bind(('', 0)) # localhost, first free port
        except:
            print("Couldn't find any available port")

        self.end = True # the udp sesson ends? True means we ended our session therefore no.

        self.mode = None # download or upload

        self.wait = {} # dict to store thread -> True/False -- so we know if we need to kill that thread or not
        self.connected = False

        self.ack = 0
        self.seq = 0
        self.current = 0 # the current data of the file to send -> only for upload mode

        self.file_name = ""
        self.data = []

        self.other_dis = False # server wants to disconnect?
        self.me_dis = False # am i want to disconnect?
        self.thread = None # what is the last thread we started to wait?
        self.pause = False # did we got to 50% and we on a pause mode?

    def init(self): # initiate
        self.end = False
        self.wait = {}
        self.connected = False
        self.other_dis = False
        self.me_dis = False
        self.ack = 0
        self.seq = 0
        self.current = 0
        self.thread = None
        self.pause = False
        threading.Thread(target=self.file_handle, args=[]).start() # handle everything you need

    def close(self): # stop the udp run of the udp connection.
        self.check_thread()
        self.end = True

    def check_thread(self): # check if there is a thread that on wait and I need to free him from that.
        if(self.thread != None):
            if (self.wait[self.thread.getName()] != None and self.wait[self.thread.getName()]):
                self.wait[self.thread.getName()] = False

    def send_resume(self): # send resume to the server, on 50% and continue the file transfer
        server_addr = (self.serverip, self.serverport)
        code = ReliableCode["ACK"]
        message = f"{code}|{self.seq}|{self.ack}"
        self.fs.sendto(message.encode(), server_addr) # we will send the last ack so he will send from that part.

        self.check_thread()
        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message])
        self.wait[self.thread.getName()] = True
        self.thread.start()

    def file_handle(self):
        server_addr = (self.serverip, self.serverport) # server ip and port.

        self.fs.sendto(ReliableCode["SYN"].encode(), server_addr) # send syn to connect with the server udp
        self.check_thread()
        self.thread = threading.Thread(target=self.timer_to_send, args=[1, ReliableCode["SYN"]])
        self.wait[self.thread.getName()] = True
        self.thread.start() # start a thread if we dont get a syn_ack send syn again

        while not self.end:
            data_coded, addr = self.fs.recvfrom(1024)

            if(addr != server_addr):
                continue

            if(self.mode == None):
                continue

            try:
                data = data_coded.decode()
            except:
                continue

            data = data.split(sep='|', maxsplit=3)

            if(data[0] == ReliableCode["SYN_ACK"]): # if we got syn_ack then we connected
                self.check_thread()
                self.connected = True
                print("Connected to server - SYN_ACK received")

                if self.mode == MODES["Upload"]: # if we on upload mode lets send the first bytes.
                    print(self.file_name)
                    try:
                        with open(f"./files/{self.file_name}", "rb") as file: # start saving all the bytes of the file
                            data_line = file.read(1024)
                            while data_line:
                                self.data.append(data_line)
                                data_line = file.read(1024)
                    except:
                        print("Error, File not found!")
                        self.close()
                        break

                    print("Start sending file")

                    if self.current == len(self.data): # if the file is empty.
                        self.seq += 1 # 1 is the way to tell the other side that we ended the byte to send.
                    else:
                        self.seq = len(self.data[self.current]) # add the size of the bytes we want to send.
                    message = "{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack) # make message of what we gonna send
                    self.fs.sendto(message.encode(), addr) # send it -> code|seq|ack
                    self.check_thread()
                    if self.current != len(self.data): # if we have something to send and not on empty file send the data
                        self.fs.sendto(self.data[self.current], addr) # sending the data
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                    else:
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message])
                    self.wait[self.thread.getName()] = True
                    self.thread.start()

                continue

            if(not self.connected): # if we got message from someone who isn't connected to us.
                print("Error, The server started to send data, and isn't connected yet!")
                self.check_thread()
                self.close()
                break

            if(data[0] == ReliableCode["ACK"]): # if we GOT ACK on something we sent.
                self.check_thread()

                if self.mode == MODES["Upload"]: # if we on a Upload mode send the data
                    seq = int(data[1])
                    ack = int(data[2])

                    if (ack != self.seq):
                        print("Lost packet")
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq,self.ack)
                        self.fs.sendto(message.encode(), addr)
                        self.fs.sendto(self.data[self.current], addr)
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                        self.wait[self.thread.getName()] = True
                        self.thread.start()
                        continue

                    self.ack = seq
                    self.current += 1
                    message = ""

                    send_the_data = True

                    if (self.current == len(self.data)):
                        self.seq += 1
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack)
                        send_the_data = False

                    else:
                        self.seq += len(self.data[self.current])
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack)

                    self.fs.sendto(message.encode(), addr)
                    if send_the_data:
                        self.fs.sendto(self.data[self.current], addr)
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                        self.wait[self.thread.getName()] = True
                    else:
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message])
                        self.wait[self.thread.getName()] = True
                    self.thread.start()


            elif(data[0] == ReliableCode["MID_PAUSE"]): # pause on 50%
                self.pause = True
                self.fs.sendto(ReliableCode["MID_PAUSE_ACK"].encode(), addr) # send that we paused on 50%
                self.notification_function("System: The file is 50% downloaded, type /resume to continue.") #update gui

            elif(data[0] == ReliableCode["Post"]): # if something is sent to us
                if (self.mode != MODES["Download"]):
                    continue

                seq = int(data[1])
                ack = int(data[2])
                self.check_thread()

                if (seq - self.ack == 1): # if the file is finished then lets disconnect and build the file in our part.
                    self.seq += 1

                    self.fs.sendto(ReliableCode["DIS"].encode(), addr)

                    self.thread = threading.Thread(target=self.timer_to_send, args=[1, ReliableCode["DIS"]])
                    self.wait[self.thread.getName()] = True
                    self.thread.start()

                    with open(f"./files/{self.file_name}", "wb") as file:
                        for line in self.data:
                            file.write(line)

                    last_part = data.pop() # lets pop the last part of the file
                    self.notification_function("System: The file is successfully downloaded - last byte: {}".format(last_part[-1:]))

                    continue

                file_data, addr = self.fs.recvfrom(1024) # receive the data, if we didn't finish the file.

                if (seq - self.ack != len(file_data) or ack != self.seq): # check if we lost a packet.
                    code = ReliableCode["ACK"]
                    message = f"{code}|{self.seq}|{self.ack}"
                    self.fs.sendto(message.encode(), addr) # if we lost a packet lets send him that we got something wrong.
                    continue

                self.ack = seq # if we didn't lost lets get the data we got and sent him a ACK for it
                self.seq += 1
                self.data.append(file_data)

                message = "{}|{}|{}".format(ReliableCode["ACK"], self.seq, self.ack)
                self.fs.sendto(message.encode(), addr)

            elif (data[0] == ReliableCode["DIS"]): # if the server wants to disconnect

                print("Server wants to disconnect")
                self.other_dis = True
                self.fs.sendto(ReliableCode["DIS_SYN"].encode(), addr)

                if self.me_dis: # if i sent him dis before lets close the session
                    print("Closing!")
                    self.close()
                    break

                self.fs.sendto(ReliableCode["DIS"].encode(), addr) # lets send him that i want to dis to
                self.check_thread()

                self.thread = threading.Thread(target=self.timer_to_send, args=[1, ReliableCode["DIS"]])
                self.wait[self.thread.getName()] = True
                self.thread.start()

            elif (data[0] == ReliableCode["DIS_SYN"]): # accepted my disconnect
                self.wait[self.thread.getName()] = False
                self.me_dis = True
                if self.other_dis: # if he sent me a disconnected request before lets close the session
                    self.close()
                    break
        print("Finished!")

    def timer_to_send(self, time_amount, data, message2= None): # a function that we call with thread to deal with timeout.
        server_addr = (self.serverip, self.serverport)
        time.sleep(time_amount)
        if (time_amount > 3):
            self.close()
            self.wait[threading.current_thread().getName()] = False

        elif(self.wait[threading.current_thread().getName()] == True):
            self.fs.sendto(data.encode(), server_addr)
            if (message2 != None):
                self.fs.sendto(message2, server_addr)
            self.timer_to_send(time_amount+0.5, data)
