code = '103'

def handleRec(data, client):
    client.connector.recieve_message(data[0], code)
