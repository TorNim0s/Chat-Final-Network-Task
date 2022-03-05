from unittest import TestCase
from Client import ClientSide,Connector
import socket
import time

class TestClient(TestCase):
    ip = socket.gethostbyname(socket.gethostname())
    connector = Connector()
    client = ClientSide.Client(ip,11111, "Test", connector)


    def test_split_users(self):
        data = "accounts|eldad|ilan|test"

        self.client.split_users(data)
        result = ["eldad","ilan","test"]
        self.assertEqual(result, self.client.users)

    def test_kill(self):
        self.assertTrue(self.client.receive_thread.is_alive())
        self.client.kill()
        time.sleep(1)
        self.assertFalse(self.client.receive_thread.is_alive())

    def test_send_receive_server_data(self):
        code = ClientSide.Client.Codes["Message"]
        message = "{}|test".format(code)
        self.client.send_data(message)
        data = self.client.receive_server_data()
        self.assertEqual(data,"Test")

