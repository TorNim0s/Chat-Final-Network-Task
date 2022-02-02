import sys
import threading

from ClientSide import Client
from GUI import GUI

class Connector:

    def __init__(self):
        name = input("Enter your name: ")
        self.client = Client("192.168.56.1", 1111, name, self)
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



if __name__ == '__main__':
    connector = Connector()
