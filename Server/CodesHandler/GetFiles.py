import os
import time

MessageCode = '102'
ErrorCode = '107'


def handleRec(data, server, sock, addr):  # received an error message
    """
    read all the files in /files, start from the position the client sent
    us and give him back 10 files from that position
    """
    starts = int(data[1])
    files = os.listdir('./files')
    for i in range(starts, starts+10):
        time.sleep(0.05)
        if i >= len(files):
            break
        data = f"{MessageCode}|{files[i]}"
        server.sendmessage(sock, data.encode())
