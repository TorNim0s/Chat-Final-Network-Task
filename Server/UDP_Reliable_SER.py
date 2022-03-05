import socket
from socket import timeout
import threading
import time
from multiprocessing import Process

ReliableCode = {"ACK": '200', "SYN": '201', "SYN_ACK": '202', "Post": '203', "DIS": '204',
                "DIS_SYN": '205', "MID_PAUSE": '206', "MID_PAUSE_ACK": '207'}

class UDP_Reliable_Server:

    def __init__(self, fileport):
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.file_port = fileport
                self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.fs.bind((self.ip, self.file_port))

                break
            except:
                print("Couldn't bind to that port")

        print('IP Adress: ' + self.ip)
        print('Port Adress: ' + str(self.file_port))

        self.accepted = {}
        self.end = False

        self.init()

    def init(self):
        threading.Thread(target=self.handle_clients, args=()).start()

    def stop(self):
        self.end = True

    def kill_process(self, addr):

        if (self.accepted[addr].process != None):
            self.accepted[addr].process.terminate()
            self.accepted[addr].process = None

    def handle_clients(self):
        while not self.end:
            data_coded, addr = self.fs.recvfrom(1024)

            try:
                data = data_coded.decode()
            except:
                continue

            print(f"{data} -- from -- {addr}")

            data = data.split(sep="|", maxsplit=3)

            print(self.accepted)

            if(data[0] == ReliableCode["SYN"]):
                # self.accepted[addr] = User(0, "eldad.txt")
                self.fs.sendto(ReliableCode["SYN_ACK"].encode(), addr)
                self.accepted[addr].waiting = True
                print(f"Received SYN from {addr}")

                if self.accepted[addr].mode == User.MODES["Download"]:
                    print(f"Starting to send file to {addr}")
                    if self.accepted[addr].current == len(self.accepted[addr].data):
                        self.accepted[addr].seq += 1
                    else:
                        self.accepted[addr].seq = len(self.accepted[addr].data[self.accepted[addr].current])
                    message = "{}|{}|{}".format(ReliableCode["Post"],self.accepted[addr].seq,
                                                   self.accepted[addr].ack)
                    self.accepted[addr].waiting = True
                    self.fs.sendto(message.encode(), addr)
                    if self.accepted[addr].current != len(self.accepted[addr].data):
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr)
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message, self.accepted[addr].data[self.accepted[addr].current]))
                    else:
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                    self.accepted[addr].process.start()

                continue

            if(addr not in self.accepted):
                print(f"Receiving data from unaccepted address {addr}")
                continue

            if(data[0] == ReliableCode["ACK"]):
                self.kill_process(addr)
                self.accepted[addr].waiting = False

                if(self.accepted[addr].mode == User.MODES["Download"]):

                    seq = int(data[1])
                    ack = int(data[2])

                    if(ack != self.accepted[addr].seq):
                        print("Lost packet")
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq, self.accepted[addr].ack)
                        self.fs.sendto(message.encode(), addr)
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr)
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message, self.accepted[addr].data[self.accepted[addr].current]))
                        self.accepted[addr].process.start()
                        continue

                    if(self.accepted[addr].current >= len(self.accepted[addr].data)/2 and not self.accepted[addr].mid):
                        self.accepted[addr].mid = True
                        message = ReliableCode["MID_PAUSE"]
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                        self.accepted[addr].process.start()
                        continue

                    self.accepted[addr].ack = seq
                    self.accepted[addr].current += 1
                    message = ""

                    send_the_data = True

                    if (self.accepted[addr].current == len(self.accepted[addr].data)):
                        self.accepted[addr].seq += 1
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq, self.accepted[addr].ack)
                        send_the_data = False

                    else:
                        self.accepted[addr].seq += len(self.accepted[addr].data[self.accepted[addr].current])
                        message = "{}|{}|{}".format(ReliableCode["Post"], self.accepted[addr].seq,
                                                   self.accepted[addr].ack)

                    self.fs.sendto(message.encode(), addr)
                    if send_the_data:
                        self.fs.sendto(self.accepted[addr].data[self.accepted[addr].current], addr)
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message,
                                                                                           self.accepted[addr].data[self.accepted[addr].current]))
                    else:
                        self.accepted[addr].waiting = True
                        self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, message))
                    self.accepted[addr].process.start()


            elif(data[0] == ReliableCode["Post"]):

                if(self.accepted[addr].mode != User.MODES["Upload"]):
                    continue

                seq = int(data[1])
                ack = int(data[2])
                self.kill_process(addr)

                if (seq - self.accepted[addr].ack == 1):
                    # message = "%s|%s|%s".format(ReliableCode["ACK"], self.accepted[addr].seq, self.accepted[addr].ack)
                    # self.fs.sendto(message.encode(), addr)

                    self.fs.sendto(ReliableCode["DIS"].encode(), addr)

                    self.accepted[addr].waiting = True
                    self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, ReliableCode["DIS"]))
                    self.accepted[addr].process.start()

                    with open(f"./files/{self.accepted[addr].file_name}", "wb") as file:
                        for line in self.accepted[addr].data:
                            file.write(line)

                    print("Got the file successfully")
                    continue

                file_data, addr = self.fs.recvfrom(1024)

                if(seq - self.accepted[addr].ack != len(file_data) or ack != self.accepted[addr].seq):
                    code = ReliableCode["ACK"]
                    message = f"{code}|{self.accepted[addr].ack}"
                    self.fs.sendto(message.encode(), addr)
                    continue

                self.accepted[addr].ack = seq
                self.accepted[addr].seq += 1
                self.accepted[addr].data.append(file_data)

                message = "{}|{}|{}".format(ReliableCode["ACK"], self.accepted[addr].seq, self.accepted[addr].ack)
                self.fs.sendto(message.encode(), addr)

            elif(data[0] == ReliableCode["MID_PAUSE_ACK"]):
                self.accepted[addr].pause = True
                self.kill_process(addr)

            elif(data[0] == ReliableCode["DIS"]):
                self.kill_process(addr)

                self.accepted[addr].other_dis = True
                self.fs.sendto(ReliableCode["DIS_SYN"].encode(), addr)


                if self.accepted[addr].me_dis:
                    self.kill_process(addr)
                    self.accepted.__delitem__(addr)
                    continue

                self.fs.sendto(ReliableCode["DIS"].encode(), addr)
                self.accepted[addr].waiting = True
                self.accepted[addr].process = Process(target=self.timer_to_send, args=(addr, 1, ReliableCode["DIS"]))
                self.accepted[addr].process.start()

            elif(data[0] == ReliableCode["DIS_SYN"]):
                self.kill_process(addr)
                self.accepted[addr].waiting = False
                self.accepted[addr].me_dis = True
                if self.accepted[addr].other_dis:
                    self.kill_process(addr)
                    self.accepted.__delitem__(addr)
                    continue

    def timer_to_send(self, addr, time_amount, data, message2= None):
        time.sleep(time_amount)
        if (time_amount > 3):
            self.accepted[addr].waiting = False
            self.accepted.__delitem__(addr)
            self.kill_process(addr)

        elif(self.accepted[addr].waiting == True):
            self.fs.sendto(data.encode(), addr)
            if(message2 != None):
                self.fs.sendto(message2, addr)
            self.timer_to_send(addr, time_amount+0.5, data)

class User:
    MODES = {"Download":0, "Upload":1}

    def __init__(self, mode, file_name):
        self.waiting = False
        self.seq = 0
        self.ack = 0
        self.mode = mode
        self.current = 0
        self.file_name = file_name
        self.data = []
        self.process = None

        with open(f"./files/{self.file_name}", "rb") as file:
            data_line = file.read(1024)
            while data_line:
                self.data.append(data_line)
                data_line = file.read(1024)


        self.other_dis = False
        self.me_dis = False
        self.mid = False
        self.pause = False
# if __name__ == '__main__':
#     server = UDP_Reliable_Server()