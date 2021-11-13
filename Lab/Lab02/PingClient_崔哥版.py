#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time
import math
import socket


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# socket timeout 600ms
TIME_OUT = 600

# ping times
COUNT_OF_PING = 15


def ping(Socket: socket.socket, Address: tuple, Numbers: int) -> list:
    rtt_list = []
    server_address = ()
    # where sequence_number starts at 3,331 and progresses to 3,345
    # for each successive ping message sent by the client
    # i \in [3331, 3346)
    for i in range(3331, 3331 + Numbers):
        send_time = time.time()
        message = "PING " + str(i) + " " + str(send_time) + "\r\n"

        Socket.sendto(message.encode('utf-8'), Address)

        output = "ping to {}, seq = {}, {}"

        try:
            modified_message, server_address = Socket.recvfrom(2048)
            reply = (modified_message.decode('utf-8')).split()
            recv_time = time.time()
        except socket.timeout:
            print(output.format(server_address[0], i, "time out"))
            continue

        rtt = recv_time - send_time
        rtt_list.append(rtt)
        rtt_string = "rtt = " + str(round((rtt) * 1E3, 3)) + " ms"
        print(output.format(server_address[0], i, rtt_string))

    return rtt_list


def main(Argument: list) -> int:

    # Get command line argument.
    if (len(Argument) != 3):
        print("Error: Required host and port")
        return EXIT_FAILURE

    # Define connection (socket) parameters,
    server_name, server_port = Argument[1], int(Argument[2])
    if (server_name == "localhost"):
        server_name = "127.0.0.1"

    # Define address
    address = (server_name, server_port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIME_OUT / 1E3)

    ping_times = COUNT_OF_PING

    rtt_list = ping(client_socket, address, ping_times)

    # Close the socket
    client_socket.close()

    received = len(rtt_list)
    total_time = round(sum(rtt_list) * 1E3, 3)
    max_rtt = round(max(rtt_list) * 1E3, 3)
    min_rtt = round(min(rtt_list) * 1E3, 3)
    loss_ratio = round(((15 - received) / 15) * 1E2, 2)
    avg_rtt = round(total_time / received, 3)
    # mdev = sqrt(sum(RTT*RTT) / N – (sum(RTT)/N)^2)
    a = sum(list(map(lambda x: x * x, rtt_list))) / received
    b = pow(sum(rtt_list) / received, 2)
    mdev = round(math.sqrt(a - b), 3)

    report = f"""
--- {address[0]} ping statistics ---
{ping_times} packets transmitted, {received} received, {loss_ratio} % packet loss, time {total_time} ms
rtt min/avg/max/mdev = {min_rtt}/{avg_rtt}/{max_rtt}/{mdev} ms
        """

    print(report)

    # exit success
    return EXIT_SUCCESS


if __name__ == "__main__":
    main(sys.argv)
