code = '107'
MessageCode = '102'

def handleRec(data, server, sock, addr):  # received an error message
    print(f"Error: {data[1]}")
