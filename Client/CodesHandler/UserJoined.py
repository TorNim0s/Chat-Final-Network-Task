def handleRec(data, client):
    client.users.append(data[0])
    print(f"{data[0]} joined the chat")
    client.connector.recieve_message(f"{data[0]} joined the chat")
    client.connector.update_users(client.users)