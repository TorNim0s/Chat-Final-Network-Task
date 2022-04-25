import sys
import threading
import socket
from ClientSide import Client
from GUI import GUI
from LoginGUI import LoginGUI

class Connector:

    def __init__(self):
        self.name = ""
        self.ip = ""
        self.port = 0
        self.Login = LoginGUI(self) # starting with login gui and passing him this connector
        self.Login.init()
        # this will be called only after login
        self.client = Client(self.ip, self.port, self.name, self) # Client functionality different thread
        self.gui = GUI(self) # GUI functionality
        self.gui.init() # init the gui (color the screen and layouts)
        self.data = [] # data to be displayed in gui
        self.users = [] # users to be displayed in gui
        self.gui.start() # start the gui
        self.client.kill() # kill the client thread (this will be called only when the gui is closed)

    def update_users(self, users): # update the users list in GUI
        self.users = users
        self.gui.update_users(users)

    def send_message(self, message): # send normal message to server
        self.client.send_data(message, Client.Codes["Message"])

    def send_private_message(self, message, user): # send private message to user
        message = f"{user}|{message}"
        self.client.send_data(message, Client.Codes["PrivateMessage"])

    def recieve_message(self, message, code=0): # recieve message from server
        # insert message to data (in the start so it will show as the first in the gui)
        if code == Client.Codes["PrivateMessage"]:
            self.data.insert(0, f"*Private* {message}") # insert private before the message if its private
        elif code == Client.Codes["Error"]:
            self.data.insert(0, f"*Error* {message}") # insert error before the message if its error
        else:
            self.data.insert(0, message)
        self.gui.update(message) # update the gui with the new message

    def get_files(self, data): # get list of files that on server
        self.client.send_data(data, Client.Codes["GetFiles"])

    def send_file(self, data): # send file to server
        self.client.send_data(data, Client.Codes["UploadFile"])

    def download_file(self, data): # download file from server
        self.client.send_data(data, Client.Codes["DownloadFile"])

    def set_client_info(self, name, ip, port): # for LoginGUI to set client info
        self.name = name
        self.ip = ip
        self.port = port


if __name__ == '__main__':
    connector = Connector()
