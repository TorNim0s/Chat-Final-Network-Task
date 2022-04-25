from CodesHandler import UserJoined, UserLeft, Message, \
    PrivateMessage, UploadFile, DownloadFile, GetFiles, Error

# Codes and Handler between Client and Server, used to handle the messages
Codes = {"UserJoined": '100', "UserLeft": '101', "Message": '102', "PrivateMessage": '103', "UploadFile": '104',
         "DownloadFile": '105', "GetFiles": '106', "Error": '107'}

# Handler for the different codes, each one handles a different message
# for example Handler[Codes{"UserJoined"}].handleRec will handle the received message with code UserJoined(100)
Handler = {Codes["UserJoined"]: UserJoined, Codes["UserLeft"]: UserLeft, Codes["Message"]: Message,
           Codes["PrivateMessage"]: PrivateMessage, Codes["UploadFile"]: UploadFile,
           Codes["DownloadFile"]: DownloadFile, Codes["GetFiles"]: GetFiles,
           Codes["Error"]: Error}


class CodeHandlerSwitcher:

    def __init__(self, client):
        self.client = client # the client so we can send messages throw him to the server

    def handleCodeReceive(self, code: str, data: str): # handles the received message
        data = data.split(sep="|", maxsplit=1)
        Handler[code].handleRec(data, self.client)

    def handleCodeSend(self, code: str, data: str): # handles the message to send
        # we want to handle download and upload differently, so we split the function
        # for the other codes we have same functionality therefore we don't send them all for their own handler
        if code == Codes["DownloadFile"] or code == Codes["UploadFile"]:
            Handler[code].handleSend(data, self.client) # handle download or upload
        else:
            data = code + "|" + data # add the code to the message.
            self.client.s.send(data.encode()) # send the message to the server


