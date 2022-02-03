import sys
import threading
import socket
from ClientSide import Client
from GUI import GUI
from LoginGUI import LoginGUI

class Connector:

    def __init__(self):
        self.name = "Dan"
        self.ip = "localhost"
        self.port = 1111
        self.Login = LoginGUI(self)
        self.Login.init()
        self.client = Client(self.ip, self.port, self.name, self)
        self.gui = GUI(self)
        self.gui.init()
        self.data = []
        self.users = []
        self.gui.start()
        self.client.kill()

    def update_users(self, users):
        self.users = users
        self.gui.update_users(users)

    def send_message(self, message):
        self.client.send_data(message)

    def recieve_message(self, message):
        self.data.insert(0, message)
        self.gui.update(message)

    def set_client_info(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port


if __name__ == '__main__':
    connector = Connector()
