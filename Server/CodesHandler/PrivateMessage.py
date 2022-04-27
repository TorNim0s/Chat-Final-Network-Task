code = '103'
MessageCode = '102'
ErrorCode = '107'

def handleRec(data, server,sock,addr):
    """
    :param data: [code,user to send to,message]
    :param server: instance of the server
    :param sock: the sock who put the request for the server
    :param addr: the address of the client who put the request for the server
    Explication:
    This function handle the request for the server to send a private message between two users.
    First we make a list of all the name of the users in the server.
    Then we check if the user who we want to send to the message is in the list of users.
    if he is then we get his socket and send him the private message.
    """
    message = data[2]
    name = data[1]

    key_list = list(server.connections.keys())
    val_list = list(server.connections.values())

    try:
        position = val_list.index(name)
        send_sock = key_list[position]
        private_message(server, sock, send_sock, message.encode())
    except ValueError:
        print("User %s not found".format(name))
        server.sendmessage(sock, f"{ErrorCode}|User not found".encode())

def private_message(server, my_sock, send_sock, data):
    """
    :param server: instance of the server
    :param my_sock: the source of the message
    :param send_sock: the destination of the message
    :param data: the data we want to send
    """
    try:
        # setting the data to be sent to the destination
        dataTo = f"{code}|From {server.connections[my_sock]}: {data.decode()}".encode()

        # setting the data to be sent to the source
        dataFrom = f"{code}|To {server.connections[send_sock]}: {data.decode()}".encode()

        send_sock.send(dataTo) # to the destination

        if my_sock != server.s: # if the source isn't the server than send it to the source
            my_sock.send(dataFrom)
    except:
        print("Error sending data to %s" % (server.connections[send_sock]))