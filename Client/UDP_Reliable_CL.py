import socket
from socket import timeout
import threading
import time
from multiprocessing import Process

ReliableCode = {"ACK": '200', "NACK": '201', "SYN": '202', "SYN_ACK": '203', "Post": '204', "DIS": '205',
                "DIS_SYN": '206'}

ReadSize = 1000 # read 1000 bytes from file each time
MODES = {"Download": 0, "Upload": 1}

class UDP_Reliable_Client:
    def __init__(self, serverip, serverport):
        self.serverip = serverip
        self.serverport = serverport
        try:
            self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.fs.bind(('', 0))
        except:
            print("Couldn't find any available port")

        self.end = True

        self.mode = None # needs to get a mode

        self.wait = False
        self.connected = False

        self.ack = 0
        self.seq = 0
        self.current = 0

        self.file_name = ""
        self.data = []

        self.other_dis = False
        self.me_dis = False
        self.process = None

    def init(self):
        self.end = False
        self.wait = False
        self.connected = False
        self.other_dis = False
        self.me_dis = False
        self.ack = 0
        self.seq = 0
        self.current = 0
        self.process = None
        Process(target=self.file_handle, args=()).start()

    def close(self):
        self.check_process()
        self.end = True

    def check_process(self):
        print(self.process)
        if (self.process != None):
            self.process.terminate()
            self.process = None

    def file_handle(self):
        server_addr = (self.serverip, self.serverport)

        self.wait = True
        self.fs.sendto(ReliableCode["SYN"].encode(), server_addr)
        self.process = Process(target=self.timer_to_send, args=(1, ReliableCode["SYN"]))
        self.process.start()

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

            print(f"{data} -- from -- {addr}")

            data = data.split(sep='|', maxsplit=3)

            if(data[0] == ReliableCode["SYN_ACK"]):
                self.check_process()
                self.wait = False
                self.connected = True
                print("Connected to server - SYN_ACK received")

                if self.mode == MODES["Upload"]:
                    print("Start sending file")

                    self.seq = len(self.data[self.current])
                    message = "{}|{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack, self.data[self.current])
                    self.fs.sendto(message.encode(), addr)
                    self.current+=1
                    self.wait = True
                    threading.Thread(target=self.timer_to_send, args=(1, message)).start()
                continue

            if(not self.connected):
                print("Error, The server started to send data, and isn't connected yet!")
                self.check_process()
                self.wait = False
                self.close()
                break

            if(data[0] == ReliableCode["ACK"]):
                self.check_process()
                self.wait = False

                if self.mode == MODES["Upload"]:
                    seq = data[1]
                    ack = data[2]

                    self.ack = seq

                    if(ack != self.seq):
                        message = "{}|{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack, self.data[self.current])
                        self.fs.sendto(message.encode(), addr)
                        continue

                    self.current += 1
                    if (self.current < len(self.data)):
                        self.seq += len(self.data[self.current])

                    message = ""

                    if(self.current == len(self.data)):
                        message = "{}|{}|{}|0".format(ReliableCode["Post"], self.seq, self.ack)
                    else:
                        message = "{}|{}|{}|{}".format(ReliableCode["Post"], self.seq, self.ack, self.data[self.current])

                    self.fs.sendto(message.encode(), addr)
                    self.wait = True
                    threading.Thread(target=self.timer_to_send, args=(1, message)).start()

            elif(data[0] == ReliableCode["Post"]):
                if (self.mode != MODES["Download"]):
                    continue

                seq = int(data[1])
                ack = int(data[2])

                if (seq - self.ack == 1):
                    self.seq += 1
                    # message = "{}|{}|{}".format(ReliableCode["ACK"], self.seq, self.ack)
                    # self.fs.sendto(message.encode(), addr)


                    self.fs.sendto(ReliableCode["DIS"].encode(), addr)
                    self.waiting = True

                    self.check_process()

                    self.process = Process(target=self.timer_to_send, args=(1, ReliableCode["DIS"]))
                    self.process.start()

                    with open(self.file_name, "wb") as file:
                        for line in self.data:
                            file.write(line)

                    continue

                file_data, addr = self.fs.recvfrom(1024)

                if (seq - self.ack != len(file_data) or ack != self.seq):
                    code = ReliableCode["ACK"]
                    message = f"{code}|{self.seq}|{self.ack}"
                    self.fs.sendto(message.encode(), addr)
                    continue

                self.ack = seq
                self.seq += 1
                self.data.append(file_data)

                message = "{}|{}|{}".format(ReliableCode["ACK"], self.seq, self.ack)
                self.fs.sendto(message.encode(), addr)

            elif (data[0] == ReliableCode["DIS"]):

                print("Other wants to disconnect")
                self.other_dis = True
                self.fs.sendto(ReliableCode["DIS_SYN"].encode(), addr)

                if self.me_dis:
                    print("Closing!")
                    self.close()
                    break

                self.fs.sendto(ReliableCode["DIS"].encode(), addr)
                self.waiting = True
                self.check_process()

                self.process = Process(target=self.timer_to_send, args=(addr, 1, ReliableCode["DIS"]))
                self.process.start()

            elif (data[0] == ReliableCode["DIS_SYN"]):
                self.waiting = False
                self.me_dis = True
                if self.other_dis:
                    self.close()
                    break
        print("Finished!")

    def timer_to_send(self, time_amount, data):
        server_addr = (self.serverip, self.serverport)

        time.sleep(time_amount)
        print("STILL IN HERE")
        if (time_amount > 3):
            self.close()
            self.wait = False

        elif(self.wait == True):
            self.fs.sendto(data.encode(), server_addr)
            self.timer_to_send(time_amount+0.5, data)

if __name__ == '__main__':
    client = Client()
    client.init()