code = '105' # tcp chat code
mode = 0 # udp reliable mode code

def handleRec(data, client):
    if (data[0] == "OK"):
        client.udp_reliable_connection.init()

def handleSend(data, client):
    client.udp_reliable_connection.file_name = data
    client.udp_reliable_connection.mode = mode
    data = f"{data}|{client.udp_reliable_connection.fs.getsockname()[1]}"  # add the udp port to the packet
    data = code + "|" + data  # add the code to the message.
    client.s.send(data.encode())