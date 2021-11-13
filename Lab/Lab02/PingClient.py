from math import sqrt
import socket
import time
import sys

# check the arguments number
if len(sys.argv) != 3:
    print("Argument Error: Require 3 args. Check your host and port.")
    sys.exit()

packets_sent = 15

address = sys.argv[1] if sys.argv[1] != "localhost" else "127.0.0.1"
port = sys.argv[2]

transmitted_times = []
time_started = time.time()

for i in range(0,packets_sent):
    message = "PING {} {}\r\n".format(i, int(time.time()))
    sendtime = time.time()
    message = message.encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.6)

    timeout = False
    sock.sendto(message, (address, int(port)))
    try:
        received = sock.recvfrom(1024)
    except Exception as exception:
        timeout = True
    receivetime = time.time()

    time_used = (receivetime - sendtime) * 1000

    if timeout == False:
        print("ping to {}, seq = {}, rtt = {:.2f} ms".format(address, i, time_used))
        transmitted_times.append(time_used)
    else:
        print("ping to {}, seq = {}, rtt = Timeout".format(address, i))

time_ended = time.time()

# mdev = sqrt(sum(RTT*RTT) / N – (sum(RTT)/N)^2)
a = sum(list(map(lambda x:x*x, transmitted_times))) / len(transmitted_times)
b = pow(sum(transmitted_times) / len(transmitted_times), 2)

print("\n--- {} ping statistics ---".format(address))
print("{} packets transmitted, {} received, {:.3f}% packet loss, time {:.0f}ms".format(packets_sent, len(transmitted_times), (packets_sent - len(transmitted_times))/packets_sent * 100, (time_ended - time_started) * 1000))
print("rtt min/avg/max/mdev = {:.3f}/{:.3f}/{:.3f}/{:.3f} ms".format(min(transmitted_times), sum(transmitted_times) / packets_sent, max(transmitted_times), sqrt(a-b)))