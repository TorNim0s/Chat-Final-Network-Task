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
                self.port = 1111 # port number

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket AF_INET = IPV4 , socket type = TCP.
                self.s.bind((self.ip, self.port)) # bind the socket to the port. if the port is already has been socketed it will send error.

                self.file_port = 2222
                # self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # self.fs.bind((self.ip, self.file_port))

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

            print(client_name.decode());
            self.connections[c] = client_name.decode()

            data = "accounts|" + "|".join(self.connections.values())

            c.send(data.encode())

            name = client_name.decode()
            data = f"{name}"
            self.broadcast(c, data.encode(), Codes["UserJoined"])

            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def broadcast(self, sock, data, code):
        data = f"{code}|{data.decode()}".encode()
        # print(data.decode())
        for client, name in self.connections.items():
            if client != self.s:
                if code == Codes["UserJoined"] or code == Codes["UserLeft"]:
                    if client != sock:
                        self.sendmessage(client, data)
                else:
                    self.sendmessage(client ,data)

    def sendmessage(self, sock, data):
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

    def handle_client_file(self, sock, data, code, addr, name):
        try:
            # data = c.recv(1024)
            # data = data.decode()
            print(data)
            data = data.split("|")
            if code == Codes["DownloadFile"]:
                file_name = data[1]
                addr = (addr[0], int(data[2]))
                try:
                    user = UDP_Reliable_SER.User(UDP_Reliable_SER.User.MODES["Download"], file_name)
                    self.udp_reliable.accepted[addr] = user
                    ok_message = f"{Codes['DownloadFile']}|OK"
                    self.sendmessage(sock, ok_message.encode())
                    # try:
                #     with open(file_name, "rb") as f:
                #         file_data = f.read(1024)
                #         while file_data:
                #             if (self.fs.sendto(file_data, addr)):
                #                 print("Sending file to %s" % (name))
                #                 file_data = f.read(1024)
                except FileNotFoundError:
                    print("File not found")
                    error = f"{Codes['Error']}|Server: File not found"
                    self.sendmessage(sock, error.encode())
                    # self.PrivateMessage(self.s, sock, f"Server: File {file_name} is not in the server".encode())

                # file_data = file_data.encode() # change this to get the file data
                # self.fs.sendto(file_data, addr)
                # print(f"File {file_name} has been sent to {addr[0]}")
                # self.PrivateMessage(self.s, sock, f"Server: File {file_name} is has succesfully sent to you!".encode())

            elif code == Codes["UploadFile"]:
                file_name = data[1]
                file_size = data[2]
                print("Saving file %s" % file_name)
                with open(file_name, 'wb') as f:
                    file_data = self.fs.recv(1024)
                    while file_data:
                        f.write(file_data)
                        self.fs.settimeout(2)
                        file_data = self.fs.recv(1024)
                # file_data = self.fs.recv(1024)
                # print(f"File {file_name} has been sent to {addr[0]}")
                # self.sendmessage(c, file_data)
                print(f"File {file_name} has been received from {addr[0]} known as : {name}")
                self.broadcast(self.fs, f"Server: File {file_name} has been received from {name}".encode(),
                               Codes["Message"])
                self.files.append(file_name)


            elif code == Codes["Error"]:
                print(f"Error: {data[1]}")
                # self.fs.close()

        except timeout:
            print(f"File {file_name} has been received from {addr[0]} known as : {name}")
            self.broadcast(self.fs, f"Server: File {file_name} has been received from {name}".encode(), Codes["Message"])
            self.files.append(file_name)
            # except Exception as e:
            #     print("Error receiving data from %s:%s" % (addr[0], addr[1]))
            #     print(e)
            #     self.fs.close()
            #     break

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                data = data.decode()
                print("data recieved %s from %s" % (data, self.connections[c]))

                data_splited = data.split(sep="|", maxsplit=2)

                # print(data_splited)

                # data = data.encode()
                if data_splited[0] == Codes["Message"]:
                    data = f"{self.connections[c]}: {data_splited[1]}"
                    self.broadcast(c, data.encode(), code=Codes["Message"])
                elif data_splited[0] == Codes["UploadFile"] or data_splited[0] == Codes["DownloadFile"]:
                    self.handle_client_file(c, data, data_splited[0], addr, self.connections[c])
                elif data_splited[0] == Codes["GetFiles"]:
                    starts = int(data_splited[1])
                    files = os.listdir('./files')
                    print (files)
                    for i in range(starts, starts+10):
                        time.sleep(0.05)
                        if i >= len(files):
                            break
                        data = f"{Codes['Message']}|{files[i]}"
                        self.sendmessage(c, data.encode())

                elif data_splited[0] == Codes["PrivateMessage"]:
                    data = f"{self.connections[c]}: {data_splited[2]}"
                    name = data_splited[1]

                    # try:

                    key_list = list(self.connections.keys())
                    val_list = list(self.connections.values())

                    position = val_list.index(name)
                    sock = key_list[position]

                    self.PrivateMessage(c, sock ,data.encode())
                    # except:
                    #     print("User is not in the server")

            except socket.error:
                name = self.connections[c]
                data = f"{name}"
                self.broadcast(c, data.encode(), Codes["UserLeft"])
                self.connections.__delitem__(c)
                c.close()
                break

if __name__ == '__main__':
    server = Server()
