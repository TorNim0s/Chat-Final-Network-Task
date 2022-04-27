import socket
from socket import timeout
import threading
import time
import os
import UDP_Reliable_SER
from CodeHandler import CodeHandlerSwitcher

"""
Create a server with a socket and a thread
max 24 clients can connect to the server at the same time

*Important*: The server is running both udp and tcp sockets at the same time. (2 threads)

"""

# Unique Codes for communication between the server and the client
Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
         "DownloadFile": '105', "GetFiles":'106', "Error": '107'}

class Server:

    def __init__(self):
        self.codeHandler = CodeHandlerSwitcher(self)
        self.ip = socket.gethostbyname(socket.gethostname()) # get ip of the server
        while 1: # infinite loop
            try:
                self.port = 11111 # port number

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket AF_INET = IPV4 , socket type = TCP.
                self.s.bind((self.ip, self.port)) # bind the socket to the port. if the port is already has been socketed it will send error.

                self.filePort = 50000 # port for the udp socket (file transfer)

                break
            except:
                print("Couldn't bind to that port")

        print('IP Adress: ' + self.ip) # print ip of the server
        print('Port Adress: ' + str(self.port)) # print port of the server

        self.files = [] # list of files
        self.connections = {} # dict --> (sock -> name)
        # udpReliable auto start (different thread)
        self.udpReliable = UDP_Reliable_SER.UDP_Reliable_Server(self.filePort) # instance of the udp reliable server
        self.accept_connections() # main function

    def accept_connections(self): # Handles connections from clients, accept them and open a new thread to handle them
        self.s.listen(24) # maximum client to listen
        while True:
            c, addr = self.s.accept() # accept a new connection
            print("Accepted a connection request from %s:%s" % (addr[0], addr[1]))

            c.send(str(self.filePort).encode()) # send the new connection our file port

            client_name = c.recv(1024) # receiving the name of the client

            self.connections[c] = client_name.decode() # saving this name in our dict

            # adding all the names in the dict to string and sending it to the client
            data = "|".join(self.connections.values())

            c.send(data.encode()) # send him the names

            name = client_name.decode() # decode the name from bytes to string
            data = f"{name}" # changin data to be the name of the client
            # sending the other clients that a new client has joined named $name
            self.broadcast(c, data.encode(), Codes["UserJoined"])

            # start a new thread that handles that client
            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def broadcast(self, sock, data, code): # send message to everyone
        """
        :param sock: the src socket (who sent the message, who left, who joined...)
        :param data: the data to be sent
        :param code: the code of the data (100-UserJoined, 101-UserLeft,...)
        :return:
        """
        data = f"{code}|{data.decode()}".encode() # data to be sent (code|data)
        for client, name in self.connections.items(): # for each client we have
            if client != self.s: # if the client isn't the server
                if code == Codes["UserJoined"] or code == Codes["UserLeft"]: # if the code is UserJoined or UserLeft
                    if client != sock: # if the client isn't the one who sent the message (aka joined or disconnected)
                        # send the message to the client (in this case except the one who joined or left)
                        self.sendmessage(client, data)
                else:
                    self.sendmessage(client,data) # send the message to the client (in this case to everyone)

    def sendmessage(self, sock, data): # send message to a sock -> the function that actualy sends the message
        try:
            sock.send(data)
        except:
            print("Error sending data to %s" % (self.connections[sock]))

    def handle_client_file(self, sock, data, code, addr): # handles the file transfer, get filename and set the udp server side
        """
        :param sock: client socket
        :param data: the data we want to handle -> code|data|port
        :param code: code of the data
        :param addr: the address of the client (we need it for the udp server)
        :return:
        """
        data = data.split("|")
        if code == Codes["DownloadFile"]: # if we want to download a file
            print("DOWNLOADING!!")
            file_name = data[1] # get the file name (test.txt,...)
            addr = (addr[0], int(data[2])) # get the address of the client udp socket (ip, port)
            try:
                # create new instance of user udp server with Mode.Download, and the file name
                user = UDP_Reliable_SER.User(UDP_Reliable_SER.User.MODES["Download"], file_name)

                # add the client to the accepted list so the udp knows to handle him
                self.udpReliable.accepted[addr] = user

                ok_message = f"{Codes['DownloadFile']}|OK"
                self.sendmessage(sock, ok_message.encode()) # send that we ok and ready to start transfer data.

            except FileNotFoundError: # if the file doesn't exist
                print("File not found")
                error = f"{Codes['Error']}|Server: File not found"
                self.sendmessage(sock, error.encode()) # send an error message about it

        elif code == Codes["UploadFile"]: # if we want to upload a file
            print("Uploading!!")
            file_name = data[1] # get the file name (test.txt,...)
            addr = (addr[0], int(data[2])) # get the address of the client udp socket (ip, port)
            print("Saving file %s" % file_name)

            # create new instance of user udp server with Mode.Upload, and the file name
            user = UDP_Reliable_SER.User(UDP_Reliable_SER.User.MODES["Upload"], file_name)
            self.udpReliable.accepted[addr] = user # add the client to the accepted list so the udp knows to handle him
            ok_message = f"{Codes['UploadFile']}|OK"
            self.sendmessage(sock, ok_message.encode()) # send that we ok and ready to start transfer data.

    def handle_client(self, c, addr):
        """
        Main function that handles the client
        :param c: our client socket that we want to handle
        :param addr: client address
        """
        while 1:
            try:
                data = c.recv(1024) # receive data from the client (1024 bytes at a time)
                data = data.decode() # decode the data
                print("data recieved %s from %s" % (data, self.connections[c])) # logs, we can save it on a file.
                # code|data
                data_splited = data.split(sep="|", maxsplit=2)

                self.codeHandler.handleCodeReceive(data_splited, c, addr) # handle the code

            except socket.error:
                name = self.connections[c]
                data = f"{name}"
                self.broadcast(c, data.encode(), Codes["UserLeft"])
                self.connections.__delitem__(c)
                c.close()
                break

if __name__ == '__main__':
    server = Server()
