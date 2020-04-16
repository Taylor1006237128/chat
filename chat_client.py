from socket import *
from multiprocessing import Process,Queue
import sys

ADDR = ("127.0.0.1", 8888)
q = Queue(5)


def receive_message(udp_socket):
    while True:
        data, addr = udp_socket.recvfrom(4096)
        if "NO" == data.decode():
            print("您已被拉黑!")
            q.put("exit")
            sys.exit()
            return
        else:
            print(" ")
            print(data.decode(),end="")


def send_message(udp_socket, name):
    while True:
        if not q.empty():
            message = q.get()
            return
        else:
            try:
                message = input("发言:")
            except KeyboardInterrupt:
                message = "exit"
            if message == "exit":
                data = "Q " + name
                udp_socket.sendto(data.encode(), ADDR)
                sys.exit()
            data = "C %s %s" % (name, message)
            udp_socket.sendto(data.encode(), ADDR)


def main():
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    while True:
        name = input("请输入姓名:")
        message = "L " + name
        udp_socket.sendto(message.encode(), ADDR)
        data, addr = udp_socket.recvfrom(1024)
        if data == "OK".encode():
            print("您已进入聊天室")
            break
        elif data == "NO".encode():
            print("您已被拉黑!")
            return
        else:
            print(data.decode())

    p = Process(target=receive_message, args=(udp_socket,))
    p.daemon = True
    p.start()
    send_message(udp_socket, name)


if __name__ == '__main__':
    main()
