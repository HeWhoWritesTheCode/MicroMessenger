import socket
import json

HOST = "127.0.0.1"
PORT = 65432

#function for sending requests to the server
def send_request(data):
    # create a socket using IPv4 and TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server (localhost currently for development)
    sock.connect((HOST,PORT))
    # send the specified data as UTF-8 binary to the server
    sock.sendall(data.encode())
    # response has to be a global variable so that the functions calling this
    # method can use the data received in the response
    # set 'response' to the data from the connection
    return sock.recv(1024)

# test function for carrying out 2+2
def test_function():
    # create a dictionary to hold the json request with test data and instructions
    request = {"header":{"id":"Test","request_type":"Addition Test"},"data":{"num1":2, "num2":2}}
    # convert the dictionary to a json-form string
    request = json.dumps(request)
    # pass the json to the send_request function so that the request will be sent to the server
    response = send_request(request)
    # return the server response, which should be the result of the calculation
    return response

# run the test function with test data 2 and 2 and print the result
print(test_function())
