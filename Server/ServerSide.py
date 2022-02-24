import socket
import threading
import sys
import select

"""
Create a server with a socket and a thread
max 24 clients can connect to the server at the same time
"""

Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UplodeFile": '104',
         "DownloadFile": '105', "Error": '105'}

class Server:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.port = 1111 # port number

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket AF_INET = IPV4 , socket type = TCP.
                self.s.bind((self.ip, self.port)) # bind the socket to the port. if the port is already has been socketed it will send error.

                self.file_port = 2222
                self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.fs.bind((self.ip, self.file_port))

                break
            except:
                print("Couldn't bind to that port")

        print('IP Adress: ' + self.ip)
        print('Port Adress: ' + str(self.port))

        self.files = []
        self.connections = {}
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
        print(data.decode())
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
            my_sock.send(data)
            send_sock.send(data)
        except:
            print("Error sending data to %s" % (self.connections[sock]))

    def handle_client_file(self, data, code, addr):
        while True:
            try:
                print("GOT HERE3")
                # data = c.recv(1024)
                # data = data.decode()
                data = data.split("|")
                print("GOT HERE2")
                if code == Codes["DownloadFile"]:
                    file_name = data[1]
                    file_size = data[2]
                    file_data = data[3]
                    file_data = file_data.encode() # change this to get the file data
                    self.fs.sendto(file_data, addr)
                    print(f"File {file_name} has been sent to {addr[0]}")
                elif code == Codes["UplodeFile"]:
                    file_name = data[1]
                    file_size = data[2]
                    print("GOT HERE")
                    with open(file_name, 'wb') as f:
                        file_data = self.fs.recv(1024)
                        while file_data:
                            f.write(file_data)
                            self.fs.settimeout(2)
                            file_data = self.fs.recv(1024)
                    # file_data = self.fs.recv(1024)
                    # print(f"File {file_name} has been sent to {addr[0]}")
                    # self.sendmessage(c, file_data)


                elif code == Codes["Error"]:
                    print(data[1])
                    self.fs.close()
                    break
            except timeout:
                print(f"File {file_name} has been received from {addr[0]}")
                self.files.append(file_name)
                break
            except:
                print("Error receiving data from %s:%s" % (addr[0], addr[1]))
                self.fs.close()
                break

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                data = data.decode()
                print("data recieved %s from %s" % (data, self.connections[c]))

                data_splited = data.split(sep="|", maxsplit=2)

                print(data_splited)

                # data = data.encode()
                if data_splited[0] == Codes["Message"]:
                    data = f"{self.connections[c]}: {data_splited[1]}"
                    self.broadcast(c, data.encode(), code=Codes["Message"])
                elif data_splited[0] == Codes["UplodeFile"]:
                    threading.Thread(target=self.handle_client_file, args=(data, data_splited[0], addr,)).start()
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
