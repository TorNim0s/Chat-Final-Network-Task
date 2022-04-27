from CodesHandler import Message, PrivateMessage, UploadFile, DownloadFile,GetFiles, Error

# Handler for the different codes, each one handles a different message
# for example Handler[Codes{"UserJoined"}].handleRec will handle the received message with code UserJoined(100)

Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
         "DownloadFile": '105', "GetFiles":'106', "Error": '107'}

Handler = {Codes["Message"]: Message, Codes["PrivateMessage"]: PrivateMessage, Codes["UploadFile"]: UploadFile,
           Codes["DownloadFile"]: DownloadFile, Codes["GetFiles"]: GetFiles, Codes["Error"]: Error}


class CodeHandlerSwitcher:

    def __init__(self, server):
        self.server = server # the server so we can send messages throw him to the client

    def handleCodeReceive(self, data: [], sock, addr): # handles the received message
        """
        :param code: code of the message
        :param data: data of the message
        :param sock: the socket of the client
        """
        Handler[data[0]].handleRec(data, self.server, sock, addr)


