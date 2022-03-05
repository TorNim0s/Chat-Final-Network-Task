import pygame
from pygame import *
import socket
import threading
from socket import timeout
import UDP_Reliable_CL

class Client:
    Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
             "DownloadFile": '105', "GetFiles": '106', "Error": '107'}

    def __init__(self, ip, port, name, connector):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector = connector
        self.stop = False
        try:
            self.target_ip = ip
            self.target_port = int(port)
            self.name = name

            self.users = []

            self.s.connect((self.target_ip, self.target_port))
        except:
            print("Couldn't connect to server")
            exit(1)

        self.file_addr = (self.target_ip, int(self.s.recv(1024).decode())) # getting the udp port of the server for the files transfer
        self.udp_reliable_connection = UDP_Reliable_CL.UDP_Reliable_Client(self.file_addr[0], self.file_addr[1], self.connector.recieve_message)

        self.s.send(self.name.encode()) # sending my name to the server so everyone will know who just connected
        self.users = []
        data_users = self.s.recv(1024).decode() # getting the users on the server
        self.split_users(data_users)

        self.connector.users = self.users

        print("Connected to Server")

        self.receive_thread = threading.Thread(target=self.receive_server_data).start() # TCP Thread receiving data

    def kill(self): # stop the tcp receiving data thread. - disconnect from the server
        self.stop = True
        self.s.close()
        # self.fs.close()
        print("Disconnected from server")

    def split_users(self, data): # when we get the users we need to split them - looks like accounts|eldad|ilan|...
        self.users = data.split("|")
        self.users.remove("accounts")

    def receive_server_data(self): # main part, the thread that receives all of the data
        while not self.stop:
            try:
                data = self.s.recv(1024)

                data = data.decode()

                data_splited = data.split(sep="|", maxsplit=2) # splitting the data because it looks like code|data

                if data_splited[0] == Client.Codes["UserJoined"]:
                    self.users.append(data_splited[1])
                    print(f"{data_splited[1]} joined the chat")
                    self.connector.recieve_message(f"{data_splited[1]} joined the chat")
                    self.connector.update_users(self.users)
                elif data_splited[0] == Client.Codes["UserLeft"]:
                    self.users.remove(data_splited[1])
                    print(f"{data_splited[1]} left the chat")
                    self.connector.recieve_message(f"{data_splited[1]} left the chat")
                    self.connector.update_users(self.users)
                elif data_splited[0] == Client.Codes["Message"]:
                    if(data_splited[1] == "Test"):
                        return "Test"
                    self.connector.recieve_message(data_splited[1])
                elif data_splited[0] == Client.Codes["PrivateMessage"]:
                    self.connector.recieve_message(data_splited[1], Client.Codes["PrivateMessage"])
                elif data_splited[0] == Client.Codes["Error"]:
                    print("Error: " + data_splited[1])
                    self.connector.recieve_message(data_splited[1], Client.Codes["Error"])
                elif data_splited[0] == Client.Codes["DownloadFile"] or data_splited[0] == Client.Codes["UploadFile"]:
                    if(data_splited[1] == "OK"):
                        self.udp_reliable_connection.init()
            except:
                pass

    def send_data(self, data, code): # sending data to the server
        self.udp_reliable_connection.file_name = data
        if code == Client.Codes["DownloadFile"]:
            self.udp_reliable_connection.mode = UDP_Reliable_CL.MODES["Download"]
            data = f"{data}|{self.udp_reliable_connection.fs.getsockname()[1]}" # add the udp port to the packet
        elif code == Client.Codes["UploadFile"]:
            self.udp_reliable_connection.mode = UDP_Reliable_CL.MODES["Upload"]
            data = f"{data}|{self.udp_reliable_connection.fs.getsockname()[1]}" # add the udp port to the packet
        data = code + "|" + data # add the code to the message.
        self.s.send(data.encode())
    #
    # def send_file(self, data, path):
    #     data_splited = data.split(sep="|", maxsplit=2)
    #     filename = data_splited[1]
    #     print(f"Sending {filename}")
    #     with open(path, "rb") as f:
    #         bytes_read = f.read(1024)
    #         while (bytes_read):
    #             if (self.fs.sendto(bytes_read, self.file_addr)):
    #                 bytes_read = f.read(1024)
    #     print(f"Sent {filename}")

