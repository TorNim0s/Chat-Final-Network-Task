def handleRec(data, client): # adding the new user that joined the chat and update it on gui
    client.users.append(data[0])
    print(f"{data[0]} joined the chat")
    client.connector.recieve_message(f"{data[0]} joined the chat")
    client.connector.update_users(client.users)