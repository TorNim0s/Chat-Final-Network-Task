import socket
import threading

clients = []

"""
Create a server with a socket and a thread
max 24 clients can connect to the server at the same time
"""

Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102'}

class Server:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.port = 1111 # port number

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket AF_INET = IPV4 , socket type = TCP.
                self.s.bind((self.ip, self.port)) # bind the socket to the port. if the port is already has been socketed it will send error.

                break
            except:
                print("Couldn't bind to that port")

        print('IP Adress: ' + self.ip)
        print('Port Adress: ' + str(self.port))

        self.connections = {}
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(24) # maximum client to listen

        while True:
            c, addr = self.s.accept()
            print("Accepted a connection request from %s:%s" % (addr[0], addr[1]))

            client_name = c.recv(1024)

            print(client_name.decode());
            self.connections[c] = client_name.decode()

            clients.append(client_name.decode())

            data = "accounts|" + "|".join(clients)

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

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                print("data recieved %s from %s" % (data.decode(), self.connections[c]))
                data = f"{self.connections[c]}: {data.decode()}"
                data = data.encode()
                self.broadcast(c, data, code=Codes["Message"])

            except socket.error:
                name = self.connections[c]
                data = f"{name}"
                self.broadcast(c, data.encode(), Codes["UserLeft"])
                clients.remove(self.connections[c])
                self.connections.__delitem__(c)
                c.close()
                break

if __name__ == '__main__':
    server = Server()
