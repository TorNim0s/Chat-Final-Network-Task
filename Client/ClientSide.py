import pygame
from pygame import *
from CodesHandler import *
import socket
import threading
from socket import timeout
import UDP_Reliable_CL
from CodeHandler import CodeHandlerSwitcher

"""
Explanation:
This class is the client side of the Chat.
It is responsible for the communication between the client and the server.
The data between the server and client lookes like this:
code|data
"""

class Client:

    Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
             "DownloadFile": '105', "GetFiles": '106', "Error": '107'} # Codes for tcp messages

    def __init__(self, ip, port, name, connector):
        self.codeHandler = CodeHandlerSwitcher(self) # Handler for the codes between the client and the server
        self.connector = connector # the connector that is used to connect the GUI to the functionality - MVC DP
        self.stop = False # boolean for our program to stop

        self.targetIP = ip
        self.targetPort = int(port)
        self.name = name

        self.users = []

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket ipv4 - tcp
            self.s.connect((self.targetIP, self.targetPort))
        except:
            print("Couldn't connect to server")
            exit(1)

        # getting the udp socket address from the server
        self.filePort = (int(self.s.recv(1024).decode()))

        # creating the UDP_Reliable_CL object and send him the server address and notify function when receiving data
        self.udp_reliable_connection = UDP_Reliable_CL.UDP_Reliable_Client(self.targetIP, self.filePort,
                                                                           self.connector.recieve_message)

        self.s.send(self.name.encode()) # sending my name to the server so everyone will know who just connected
        data_users = self.s.recv(1024).decode() # getting the users on the server

        self.split_users(data_users) # adding the users to the users list

        self.connector.users = self.users # updating the users list in the GUI throw the connector

        print("Connected to Server")

        self.receiveThread = threading.Thread(target=self.receive_server_data).start() # Main handle thread

    def kill(self): # stop the tcp connection and main thread. - disconnect from the server
        self.stop = True
        self.s.close()
        print("Disconnected from server")

    def split_users(self, data): # when we get the users we need to split them - looks like eldad|ilan|...
        self.users = data.split("|")

    def receive_server_data(self): # main part, the thread that receives all of the data
        while not self.stop:
            try:
                data = self.s.recv(1024) # receiving data from the server

                data = data.decode() # decoding the data
                data_splited = data.split(sep="|", maxsplit=1) # splitting the data because it looks like code|data

                self.codeHandler.handleCodeReceive(data_splited[0], data_splited[1]) # passing the data to the code handler
            except:
                pass

    def send_data(self, data, code): # sending data to the server
        self.codeHandler.handleCodeSend(code, data) # passing the data to the code handler

