def handleRec(data, client): # receive message
    client.connector.recieve_message(data[0])