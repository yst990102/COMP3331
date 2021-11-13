import socket
import sys

if len(sys.argv) < 2:
    print("Required : port namber.")
elif len(sys.argv) > 2:
    print("Too much arguments have been given.")

WebServer_Port = sys.argv[1]
WebServer_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
WebServer_Socket.bind(('localhost', int(WebServer_Port)))
WebServer_Socket.listen(0)

while 1:
    Connection_Socket , Connection_Address = WebServer_Socket.accept()
    
    try:
        request = Connection_Socket.recv(1024)
        request_content = request.decode()
        print(request_content)

        file = request_content.split()[1].replace('/','')
    
        requestFile = open(file, 'rb')
        data = requestFile.read()

        response_line = "HTTP/1.1 200 OK\r\n"
        if "html" in file:
            response_header = "Content-Type:text/html\r\n"
        elif "png" in file:
            response_header = "Content-Type:image/png\r\n"
        else:
            response_header = "Content-Type:others\r\n"

        response = (response_line + response_header + "\r\n").encode("utf-8")

    except Exception:
        response_line = "HTTP/1.1 404 Not Found\r\n"
        response_header = "Content-Type:text/html\r\n"

        data = "<h1><center>404 Not Found</center></h1>".encode("utf-8")
        response = (response_line + response_header + "\r\n" ).encode("utf-8")


    Connection_Socket.send(response)
    Connection_Socket.send(data)
    Connection_Socket.close()