import pygame
from pygame import *
import socket
import threading
from socket import timeout


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
            self.fs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.fs.bind(('', 0))
        except:
            print("Couldn't connect to server")
            exit(1)

        self.file_addr = (self.target_ip, int(self.s.recv(1024).decode()))

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
        self.fs.close()
        print("Disconnected from server")

    def split_users(self, data):
        self.users = data.split("|")
        self.users.remove("accounts")

    def receive_server_data(self):
        while not self.stop:
            try:
                data = self.s.recv(1024)

                data = data.decode()
                print(data)
                data_splited = data.split(sep="|", maxsplit=2)
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
                    self.connector.recieve_message(data_splited[1])
                elif data_splited[0] == Client.Codes["PrivateMessage"]:
                    print(data_splited[1])
                    self.connector.recieve_message(data_splited[1], Client.Codes["PrivateMessage"])
                elif data_splited[0] == Client.Codes["Error"]:
                    print("Error: " + data_splited[1])
                    self.connector.recieve_message(data_splited[1], Client.Codes["Error"])
            except:
                pass

    def send_data(self, data, code, path=None):
        if code == Client.Codes["DownloadFile"]:
            data = f"{data}|{self.fs.getsockname()[1]}"
        data = code + "|" + data
        self.s.send(data.encode())
        if (code == Client.Codes["UploadFile"]):
            threading.Thread(target=self.send_file, args=(data, path)).start()
        elif code == Client.Codes["DownloadFile"]:
            threading.Thread(target=self.receive_file, args=(data,)).start()

    def receive_file(self, data):
        data = data.split(sep="|", maxsplit=2)
        file_name = data[1]
        try:
            with open(file_name, 'wb') as f:
                file_data = self.fs.recv(1024)
                while file_data:
                    f.write(file_data)
                    self.fs.settimeout(2)
                    file_data = self.fs.recv(1024)

        except timeout:  # need to add last bit sent
            self.connector.recieve_message(f"received {file_name} successfully!", Client.Codes["Message"])
        except Exception as e:
            print(e)
            self.connector.recieve_message("Error receiving file", Client.Codes["Error"])

    def send_file(self, data, path):
        data_splited = data.split(sep="|", maxsplit=2)
        filename = data_splited[1]
        file_size = data_splited[2]
        print(f"Sending {filename}")
        # self.fs.send(filename.encode())
        # self.fs.send(file_size.encode())
        file_size = int(file_size)
        with open(path, "rb") as f:
            bytes_read = f.read(1024)
            # self.fs.send(bytes_read)
            while (bytes_read):
                if (self.fs.sendto(bytes_read, self.file_addr)):
                    bytes_read = f.read(1024)
        print(f"Sent {filename}")

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
