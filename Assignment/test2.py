from socket import socket
import socket
from time import sleep

if __name__ == "__main__":
    client02 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaddress02 = ("127.0.0.1", 13007)
    client02.bind(clientaddress02)
    
    client02.listen()
    client1_socket, client1_address = client02.accept()
    
    print("connection set up")

    data = client1_socket.recv(1024)
    print(data.decode())

    sleep(1)
    
    client1_socket.send("fuck u 2, 3311".encode())
    
    client02.close()
    