code = '105'
MessageCode = '102'
ErrorCode = '107'

def handleRec(data, server, sock, addr):
    server.handle_client_file(sock, "|".join(data), data[0], addr)