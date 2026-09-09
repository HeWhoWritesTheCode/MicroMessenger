import socket
import json
import threading

#DEFINING FUNCTIONS

# this function will start on a new thread every time a request needs to be read and handled
# in effect this is the part of the 'server listener' that handles clients
def handle_request(conn, address):
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
        # case for the test function
        case "Addition Test":
            # pass the data received to the function and send back the result
            conn.sendall(addition(data["data"]["num1"],data["data"]["num2"]))
        # default case
        case _:
            pass

# test function to be activated by the server listener
def addition(num1,num2):
    # calculate the total
    total = num1 + num2
    # put the total into a correctly formatted json response and convert to json string
    total = json.dumps({"header":{"id":"Test",},"data":{"total":total}})
    # return the encoded result
    return total.encode()

# START OF PROGRAM


# create a new socket called 'sock'. AF_INET specifies that the socket will use the IPv4 family.
# SOCK_STREAM specifies TCP connections.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to the correct address and port.
sock.bind(("127.0.0.1", 65432))
# enable the server to accpet connections from clients.
# The int 3 specifies the backlog - which I mentioned as a buffer that will hold many requests coming in at once
sock.listen(3)


# loop to accept any incoming connections
# in effect this is the listening part of the 'server listener'
while True:
    # set conn to a new socket object which can be used to send and receive data from the connection.
    conn = sock.accept()
    # create a new thread object 'thread' which will call the handle_request function to handle
    # the incomeing request with the accepted socket object as the argument
    thread = threading.Thread(target=handle_request, name="listener", args=(conn))
    # then all that needs to be done is hand off the client's connection to the thread and then loop
    # back round to wait to accept more client requests using the loop
    thread.start()
