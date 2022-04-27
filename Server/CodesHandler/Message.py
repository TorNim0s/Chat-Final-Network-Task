code = '102'
ErrorCode = '107'

def handleRec(data, server, sock, addr): # receive message and broadcast it to all
    data = f"{server.connections[sock]}: {data[1]}"
    server.broadcast(sock, data.encode(), code=code)