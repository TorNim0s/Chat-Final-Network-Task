import socket
from socket import timeout
import threading
import time
import os
import UDP_Reliable_SER

"""
Create a server with a socket and a thread
max 24 clients can connect to the server at the same time
"""

Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
         "DownloadFile": '105', "GetFiles":'106', "Error": '107'}

class Server:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.port = 11111 # port number

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket AF_INET = IPV4 , socket type = TCP.
                self.s.bind((self.ip, self.port)) # bind the socket to the port. if the port is already has been socketed it will send error.

                self.file_port = 50000

                break
            except:
                print("Couldn't bind to that port")

        print('IP Adress: ' + self.ip)
        print('Port Adress: ' + str(self.port))

        self.files = []
        self.connections = {}
        self.udp_reliable = UDP_Reliable_SER.UDP_Reliable_Server(self.file_port)
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(24) # maximum client to listen
        while True:
            c, addr = self.s.accept()
            print("Accepted a connection request from %s:%s" % (addr[0], addr[1]))

            c.send(str(self.file_port).encode())

            client_name = c.recv(1024)

            self.connections[c] = client_name.decode()

            data = "accounts|" + "|".join(self.connections.values())

            c.send(data.encode())

            name = client_name.decode()
            data = f"{name}"
            self.broadcast(c, data.encode(), Codes["UserJoined"])

            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def broadcast(self, sock, data, code): # send message to everyone
        data = f"{code}|{data.decode()}".encode()
        for client, name in self.connections.items():
            if client != self.s:
                if code == Codes["UserJoined"] or code == Codes["UserLeft"]:
                    if client != sock:
                        self.sendmessage(client, data)
                else:
                    self.sendmessage(client ,data)

    def sendmessage(self, sock, data): # send message to a sock -> the function that actualy sends the message
        try:
            sock.send(data)
        except:
            print("Error sending data to %s" % (self.connections[sock]))

    def PrivateMessage(self, my_sock, send_sock, data):
        try:
            code = Codes["PrivateMessage"]
            data = f"{code}|{data.decode()}".encode()
            if (my_sock != self.s):
                my_sock.send(data)
            send_sock.send(data)
        except:
            print("Error sending data to %s" % (self.connections[send_sock]))

    def handle_client_file(self, sock, data, code, addr, name): # handles the start of the file details, get filename and set the udp server side
        try:
            print(data)
            data = data.split("|")
            if code == Codes["DownloadFile"]:
                file_name = data[1]
                addr = (addr[0], int(data[2]))
                try:
                    user = UDP_Reliable_SER.User(UDP_Reliable_SER.User.MODES["Download"], file_name)
                    self.udp_reliable.accepted[addr] = user
                    ok_message = f"{Codes['DownloadFile']}|OK"
                    self.sendmessage(sock, ok_message.encode()) # send that we ok and ready to start transfer data.

                except FileNotFoundError:
                    print("File not found")
                    error = f"{Codes['Error']}|Server: File not found"
                    self.sendmessage(sock, error.encode())

            elif code == Codes["UploadFile"]:
                file_name = data[1]
                addr = (addr[0], int(data[2]))
                print("Saving file %s" % file_name)
                user = UDP_Reliable_SER.User(UDP_Reliable_SER.User.MODES["Upload"], file_name)
                self.udp_reliable.accepted[addr] = user
                ok_message = f"{Codes['UploadFile']}|OK"
                self.sendmessage(sock, ok_message.encode())

            elif code == Codes["Error"]:
                print(f"Error: {data[1]}")

        except timeout: # we get it if we do sock.settimeout
            print(f"File {file_name} has been received from {addr[0]} known as : {name}")
            self.broadcast(self.fs, f"Server: File {file_name} has been received from {name}".encode(), Codes["Message"])
            self.files.append(file_name)

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                data = data.decode()
                print("data recieved %s from %s" % (data, self.connections[c]))

                data_splited = data.split(sep="|", maxsplit=2)

                if data_splited[0] == Codes["Message"]:
                    data = f"{self.connections[c]}: {data_splited[1]}"
                    self.broadcast(c, data.encode(), code=Codes["Message"])
                elif data_splited[0] == Codes["UploadFile"] or data_splited[0] == Codes["DownloadFile"]:
                    self.handle_client_file(c, data, data_splited[0], addr, self.connections[c])
                elif data_splited[0] == Codes["GetFiles"]:
                    starts = int(data_splited[1])
                    files = os.listdir('./files')
                    for i in range(starts, starts+10):
                        time.sleep(0.05)
                        if i >= len(files):
                            break
                        data = f"{Codes['Message']}|{files[i]}"
                        self.sendmessage(c, data.encode())

                elif data_splited[0] == Codes["PrivateMessage"]:
                    data = f"{self.connections[c]}: {data_splited[2]}"
                    name = data_splited[1]

                    key_list = list(self.connections.keys())
                    val_list = list(self.connections.values())

                    position = val_list.index(name)
                    sock = key_list[position]

                    self.PrivateMessage(c, sock ,data.encode())

            except socket.error:
                name = self.connections[c]
                data = f"{name}"
                self.broadcast(c, data.encode(), Codes["UserLeft"])
                self.connections.__delitem__(c)
                c.close()
                break

if __name__ == '__main__':
    server = Server()
