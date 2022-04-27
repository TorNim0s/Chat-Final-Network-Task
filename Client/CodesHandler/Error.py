code = '107'

def handleRec(data, client):  # received an error message
    print("Error: " + data[0])
    client.connector.recieve_message(data[0], code)
