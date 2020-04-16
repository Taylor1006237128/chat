from socket import *
from multiprocessing import Process

HOST = "0.0.0.0"
POST = 8888
ADDR = (HOST, POST)
dict_user = {}
list_sensitive_words = ["xx", "aa", "bb", "oo"]
dict_record_of_user = {}
list_black = []


def handle_login(udp_socket, name, addr):
    if name in dict_user or "管理" in name:
        udp_socket.sendto("该用户名存在".encode(), addr)
    else:
        udp_socket.sendto(b"OK", addr)
        message = "欢迎%s进入聊天室\n发言:" % name
        for item in dict_user:
            udp_socket.sendto(message.encode(), dict_user[item])
        dict_user[name] = addr


def handle_chat(udp_socket, name, data):
    judge = 0
    for item in list_sensitive_words:
        if item in data:
            judge = 1
    message = "%s : %s\n发言:" % (name, data) if not judge else "由于%s聊天中含有敏感词汇向%s发出警告\n发言:" % (name, name)
    for item in dict_user:
        if item != name:
            udp_socket.sendto(message.encode(), dict_user[item])
    if judge:
        if dict_user[name][0] in dict_record_of_user:
            dict_record_of_user[dict_user[name][0]] += 1
        else:
            dict_record_of_user[dict_user[name][0]] = 1
        if dict_record_of_user[dict_user[name][0]] < 3:
            message_warning = "%s,由于的聊天内容中有敏感词汇,向您发出第%d警告,警告三次则不能进入聊天室\n发言:" % (name, dict_record_of_user[dict_user[name][0]])
            udp_socket.sendto(message_warning.encode(), dict_user[name])
        elif dict_record_of_user[dict_user[name][0]] >= 3:
            list_black.append(dict_user[name][0])
            message_warning = "您已被移出群聊!\n"
            udp_socket.sendto(message_warning.encode(), dict_user[name])
            del dict_user[name]


def handle_exit(udp_socket, name):
    del dict_user[name]
    data = "%s 退出聊天室\n发言:" % name
    for item in dict_user:
        udp_socket.sendto(data.encode(), dict_user[item])


def receive_request(udp_socket):
    while True:
        data, addr = udp_socket.recvfrom(1024)
        temp = data.decode().split(" ", 2)
        if addr[0] in list_black:
            udp_socket.sendto("NO".encode(),addr)
        else:
            if temp[0] == "L":
                handle_login(udp_socket, temp[1], addr)
            elif temp[0] == "C":
                handle_chat(udp_socket, temp[1], temp[2])
            elif temp[0] == "Q":
                handle_exit(udp_socket, temp[1])


def manager(udp_socket):
    while True:
        message = input("管理员消息:")
        data = "C 管理员 " + message
        udp_socket.sendto(data.encode(), ADDR)


def main():
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(ADDR)
    p = Process(target=receive_request, args=(udp_socket,))
    p.start()
    manager(udp_socket)
    p.join()


if __name__ == '__main__':
    main()
