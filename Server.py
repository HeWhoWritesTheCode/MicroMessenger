from ast import While
import socket
import json
from socketserver import _RequestType

# create a new socket called 'sock'. AF_INET specifies that the socket will use the IPv4 family.
# SOCK_STREAM specifies TCP connections.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to the correct address and port.
sock.bind(("127.0.0.1", 65432))
# enable the server to accpet connections from clients.
# The int 3 specifies the backlog - which I mentioned as a buffer that will hold many requests coming in at once
sock.listen(3)

# this function will start on a new thread every time a request needs to be read and handled
def handle_request(conn):
    # set the variable 'data' to the data received throug the connection.
    # The buffer size is 1024 as an arbitrary standard (the amound of data that can be received at once)
    # 'data' will be a bytes object
    data = conn.recv(1024)
    # decode the bytes to get the json string
    data = data.decode()
    # decode the json string to get the python dict back
    data = json.loads(data)
    # match-case used to check what the request type is and act apropriately
    match data["header"]["request_type"]:
        case "Addition Test":
            pass
        case _:
            pass

# loop to accept any incoming connections
while True:
    # set conn to a new socket object which can be used to send and receive data from the connection.
    # Address is set to the address of the connecting client
    conn, address = sock.accept()
