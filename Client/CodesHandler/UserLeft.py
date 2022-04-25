def handleRec(data, client):
    print("GOT HERE")
    client.users.remove(data[0])
    print(f"{data[0]} left the chat")
    client.connector.recieve_message(f"{data[0]} left the chat")
    client.connector.update_users(client.users)