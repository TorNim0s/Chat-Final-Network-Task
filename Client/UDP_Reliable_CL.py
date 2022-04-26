import socket
import threading
import time

"""
Explanation:
This section is for the Reliable UDP Client side using for sending and receiving files.
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
"""

ReliableCode = {"ACK": '200', "SYN": '201', "SYN_ACK": '202', "Post": '203', "DIS": '204',
                "DIS_SYN": '205', "MID_PAUSE": '206', "MID_PAUSE_ACK": '207'}

MODES = {"Download": 0, "Upload": 1}

class UDP_Reliable_Client:
    def __init__(self, serverip, serverport, notification_function):
        self.notification_function = notification_function # function to update gui
        self.serverip = serverip
        self.serverport = serverport
        try:
            self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
            self.fs.bind(('', 0)) # localhost, first free port
        except:
            print("Couldn't find any available port")

        self.end = True # the udp session ends? True means we ended our session.

        self.mode = None # download or upload

        self.wait = {} # dict to store (thread -> True/False) -- so we know if we need to kill that thread or not
        self.connected = False # connected to the server (in udp we don't have connected or not so we implement our own)

        self.ack = 0 # last ack we received
        self.seq = 0 # last seq we received
        self.current = 0 # the current data of the file to send -> only for upload mode (index in file)

        self.file_name = "" # the name of the file we want to send or receive
        self.data = [] # the data of the file we want to send or receive

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
        self.check_thread() # will close the thread if we have one running
        self.end = True # end our udp session

    def check_thread(self): # check if there is a thread that on wait if so free him.
        if(self.thread != None):
            # if we have a thread with that name and the thread is true (alive) than make it false.
            if (self.wait[self.thread.getName()] != None and self.wait[self.thread.getName()]):
                self.wait[self.thread.getName()] = False

    def send_resume(self): # send resume to the server, on 50% and continue the file transfer
        server_addr = (self.serverip, self.serverport)
        code = ReliableCode["ACK"]
        message = f"{code}|{self.seq}|{self.ack}"
        # we will send the last ack so the server will start sending the file from there.
        self.fs.sendto(message.encode(), server_addr)

        self.check_thread() # check if we have a thread running if so kill it.
        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message]) # create a new timer thread.
        self.wait[self.thread.getName()] = True # add the thread to our waiting dict and make it true (running)
        self.thread.start() # start that thread

    def file_handle(self): # main thread handle everything about uploading or downloading
        server_addr = (self.serverip, self.serverport) # server ip and port.

        self.fs.sendto(ReliableCode["SYN"].encode(), server_addr) # send syn to connect with the server udp
        self.check_thread() # check if we have a thread running if so kill it.
        self.thread = threading.Thread(target=self.timer_to_send, args=[1, ReliableCode["SYN"]]) # create a new timer thread.
        self.wait[self.thread.getName()] = True # add the thread to our waiting dict and make it true (running)
        self.thread.start() # start a thread if we dont get a syn_ack send syn again

        while not self.end: # main loop
            data_coded, addr = self.fs.recvfrom(1024) # get data from the server, and his address

            if(addr != server_addr): # we want to make sure we got the data from the server and not from another.
                continue

            if(self.mode == None): # check if we are in download or upload mode (if neither then we are in waiting for main code to change it)
                continue

            try:
                data = data_coded.decode() # sometimes we get the data of a file and not the code|seq|ack (timer is calling again).
            except:
                continue

            data = data.split(sep='|', maxsplit=3) # split the data to get the code, seq and ack.

            if(data[0] == ReliableCode["SYN_ACK"]): # if we got syn_ack then we connected
                self.check_thread() # kill the syn thread
                self.connected = True # we are connected
                print("Connected to server - SYN_ACK received")

                if self.mode == MODES["Upload"]: # if we on upload mode lets send the first bytes.
                    print(self.file_name)
                    try:
                        with open(f"./files/{self.file_name}", "rb") as file: # start saving all the bytes of the file
                            data_line = file.read(1024) # read the first 1024 bytes
                            # add all the file data to an array - every index in array contain 1024 bytes
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
                    self.check_thread() # kill thread if we have one
                    if self.current != len(self.data): # if we have something to send and not on empty file send the data
                        self.fs.sendto(self.data[self.current], addr) # sending the data
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                    else: # if we are on empty file send the empty message to finish
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message])
                    self.wait[self.thread.getName()] = True # add the thread to our waiting dict and make it true (running)
                    self.thread.start()

                continue

            if(not self.connected): # if we are not connected yet.
                print("Error, The server started to send data, and isn't connected yet!")
                self.check_thread()
                self.close()
                break

            if(data[0] == ReliableCode["ACK"]): # if we GOT ACK on something we sent.
                self.check_thread()

                if self.mode == MODES["Upload"]: # if we on a Upload mode send the data
                    seq = int(data[1]) # seq we got
                    ack = int(data[2]) # ack we got

                    if (ack != self.seq): # if we got ack that is not the same as the seq we sent
                        print("Malformed packet")
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq,self.ack) # code|seq|ack
                        self.fs.sendto(message.encode(), addr) # send code again
                        self.fs.sendto(self.data[self.current], addr) # send the data again
                        # thread for the data and the code together
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                        self.wait[self.thread.getName()] = True
                        self.thread.start()
                        continue

                    # get here only if we got the right ack
                    self.ack = seq
                    self.current += 1 # move to the next data in the array
                    message = ""

                    send_the_data = True

                    if (self.current == len(self.data)): # if the file is finished
                        self.seq += 1 # send just seq + 1 to tell the other side that we ended the byte to send.
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack)
                        send_the_data = False

                    else: # we still have data to send
                        self.seq += len(self.data[self.current])
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack)

                    self.fs.sendto(message.encode(), addr) # send the code|seq|ack
                    if send_the_data: # if we have data to send
                        self.fs.sendto(self.data[self.current], addr) # send the data
                        # thread for the data and the code together
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message,
                                                                                        self.data[self.current]])
                        self.wait[self.thread.getName()] = True
                    else:
                        # thread for the code only
                        self.thread = threading.Thread(target=self.timer_to_send, args=[1, message])
                        self.wait[self.thread.getName()] = True
                    #start the thread
                    self.thread.start()


            elif(data[0] == ReliableCode["MID_PAUSE"]): # pause on 50%
                self.pause = True
                self.fs.sendto(ReliableCode["MID_PAUSE_ACK"].encode(), addr) # send that we paused on 50%
                self.notification_function("System: The file is 50% downloaded, type /resume to continue.") #update gui

            elif(data[0] == ReliableCode["Post"]): # if something is sent to us
                if (self.mode != MODES["Download"]): # can only be happening in download mode
                    continue

                seq = int(data[1])
                ack = int(data[2])
                self.check_thread()

                if (seq - self.ack == 1): # if the file is finished then lets disconnect and build the file in our part.
                    self.seq += 1

                    self.fs.sendto(ReliableCode["DIS"].encode(), addr) # send DIS to disconnect

                    self.thread = threading.Thread(target=self.timer_to_send, args=[1, ReliableCode["DIS"]])
                    self.wait[self.thread.getName()] = True
                    self.thread.start()

                    with open(f"./files/{self.file_name}", "wb") as file: # save the file
                        for line in self.data:
                            file.write(line)

                    last_part = data.pop() # lets pop the last part of the file (required in the task)
                    self.notification_function("System: The file is successfully downloaded - last byte: {}".format(last_part[-1:]))

                    continue

                file_data, addr = self.fs.recvfrom(1024) # receive the data, if we didn't finish the file.

                if (seq - self.ack != len(file_data) or ack != self.seq): # check if we lost a packet.
                    code = ReliableCode["ACK"]
                    message = f"{code}|{self.seq}|{self.ack}"
                    self.fs.sendto(message.encode(), addr) # if we lost a packet lets send him that we got something wrong.
                    continue

                # if we didn't lost lets get the data we got and sent him a ACK for it
                self.ack = seq
                self.seq += 1
                self.data.append(file_data)

                message = "{}|{}|{}".format(ReliableCode["ACK"], self.seq, self.ack)
                self.fs.sendto(message.encode(), addr)

            elif (data[0] == ReliableCode["DIS"]): # if the server wants to disconnect

                print("Server wants to disconnect")
                self.other_dis = True
                self.fs.sendto(ReliableCode["DIS_SYN"].encode(), addr) # send the DIS_SYN to the server

                if self.me_dis: # if I sent him DIS before lets close the session
                    print("Closing!")
                    self.close()
                    break

                self.fs.sendto(ReliableCode["DIS"].encode(), addr) # send him that I want to DIS him
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
        """
        :param time_amount: how much time to wait until resend
        :param data: what data we want to send - code|seq|ack
        :param message2: what is the actual message we want to send if we have any
        Explanation:
        This function is called with thread to deal with timeout.
        We wait for time_amount seconds and if we didn't get ACK or any indicator we want we resend the message.
        The time is increased by 0.5 sec each time until we get to 3 seconds.
        """

        server_addr = (self.serverip, self.serverport)
        time.sleep(time_amount)
        if (time_amount > 3): # if we got to 3 we have a connection problem between us, and we want to close it.
            self.close()
            self.wait[threading.current_thread().getName()] = False

        elif(self.wait[threading.current_thread().getName()] == True):
            self.fs.sendto(data.encode(), server_addr)
            if (message2 != None):
                self.fs.sendto(message2, server_addr)
            self.timer_to_send(time_amount+0.5, data)
