import threading

def test():
    print(threading.current_thread().getName())

t = threading.Thread(target=test, args=())
print (t.getName())
t.start()
