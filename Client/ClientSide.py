import pygame
from pygame import *
import socket
import threading

class Client:
    Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UplodeFile": '104',
         "DownloadFile": '105', "Error": '105'}

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

        self.s.send(self.name.encode())

        # Receive data from server
        self.users = []
        data_users = self.s.recv(1024).decode()
        self.split_users(data_users)
        print(self.users)
        self.connector.users = self.users

        chunk_size = 1024  # 1024 bytes

        print("Connected to Server")

        # start threads
        self.receive_thread = threading.Thread(target=self.receive_server_data).start()
        # self.send_thread = threading.Thread(target=self.send_data_to_server).start()


    def kill(self):
        self.stop = True
        self.s.close()
        print("Disconnected from server")

    def split_users(self, data):
        self.users = data.split("|")
        self.users.remove("accounts")

    def receive_server_data(self):
        while not self.stop:
            try:
                data = self.s.recv(1024)

                data = data.decode()
                # print(data)
                data_splited = data.split(sep="|" , maxsplit=2)
                # print(data_splited)
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
                    print("Hi BRO IM HERE")
                    print(data_splited[1])
                    self.connector.recieve_message(data_splited[1])
                elif data_splited[0] == Client.Codes["PrivateMessage"]:
                    print(data_splited[1])
                    self.connector.recieve_message(data_splited[1], Client.Codes["PrivateMessage"])
            except:
                pass

    def send_data(self, data, code):
        data = code + "|" + data
        self.s.send(data.encode())

    # def send_data_to_server(self):
    #     while not self.stop:
    #         try:
    #             data = input("")
    #             self.s.send(data.encode())
    #         except:
    #             print("Couldn't send data to server")


# if __name__ == '__main__':
#     ip = input("IP: ")
#     port = input("Port: ")
#     name = input("Name: ")
#
#     Client(ip, port, name)