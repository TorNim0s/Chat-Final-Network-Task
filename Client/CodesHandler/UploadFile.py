code = '104' # tcp chat code
mode = 1 # udp reliable mode code

def handleRec(data, client): # recieve ok for upload file (want to start our udp connection)
    if (data[0] == "OK"):
        client.udp_reliable_connection.init()

def handleSend(data, client): # set up our udp connection (filename, mode)
    """
    :param data: file name
    :param client: our client instance
    """
    client.udp_reliable_connection.fileName = data
    client.udp_reliable_connection.mode = mode
    data = f"{data}|{client.udp_reliable_connection.fs.getsockname()[1]}"  # add the udp port to the packet
    data = code + "|" + data  # add the code to the message.
    client.s.send(data.encode())