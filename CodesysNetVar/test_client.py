import socket
import sys
import time

HOST, PORT = "127.0.0.1", 1202
data = " ".join(['hello', 'world'])

# SOCK_DGRAM - тип сокета, используемый для UDP сокетов
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Как видно, вызов connect() отсутствует; UDP не имеет соединений. Вместо этого
# данные отправляются непосредственно получателю через sendto().
for _ in range(2):
    sock.sendto(bytes(data + "\n", "utf-8"), (HOST, PORT))
    time.sleep(0.1)
    # received = str(sock.recv(1024), "utf-8")

    print("Sent:     {}".format(data))
    # print("Received: {}".format(received))
