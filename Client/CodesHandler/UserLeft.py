def handleRec(data, client): # removing the user that left the chat and update it on gui
    print("GOT HERE")
    client.users.remove(data[0])
    print(f"{data[0]} left the chat")
    client.connector.recieve_message(f"{data[0]} left the chat")
    client.connector.update_users(client.users)