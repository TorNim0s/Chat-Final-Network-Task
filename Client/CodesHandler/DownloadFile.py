code = '105' # tcp chat code
mode = 0 # udp reliable mode code

def handleRec(data, client): # recieve ok for upload file (want to start our udp connection)
    if (data[0] == "OK"):
        client.udp_reliable_connection.init()

def handleSend(data, client):
    """
    :param data: file name
    :param client: our client instance
    """
    client.udp_reliable_connection.fileName = data # set in the udp_reliable_connection the file name
    client.udp_reliable_connection.mode = mode # set in the udp_reliable_connection the mode
    data = f"{data}|{client.udp_reliable_connection.fs.getsockname()[1]}"  # add the udp port to the packet
    data = code + "|" + data  # add the code to the message.
    client.s.send(data.encode()) # send code|file_name|port