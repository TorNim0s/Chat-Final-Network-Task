code = '103'

def handleRec(data, client): # recieve private message
    client.connector.recieve_message(data[0], code)
