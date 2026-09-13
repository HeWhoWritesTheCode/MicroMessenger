import socket # needed for using sockets for networking
import json # needed to convert dicts to json form
            # (this is useful since it can convert variables to their values in the json string)
import PySimpleGUI as sg # needed for the GUI; abbreviated for ease of use


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
    # decode the response bytes
    response.decode()
    # convert the json into a dictionary so data can be accessed more easily
    response = json.loads(response)
    # return the data stored in the json response
    return response["data"]["total"]

# run the test function with test data 2 and 2 and print the result
# print(test_function())

# direct chat left column
dc_column = [
    [sg.Text("Chats",font=(None,25),auto_size_text=False)], # title text element
    [sg.Button("Test Chat",auto_size_button=False,size=(22,2),font=(None,12))] # button to represent chat selection
]

# this array will hold all of the elements for the window
layout =[
    [sg.Column(dc_column,expand_y=True,size=(None,100)), sg.VerticalSeparator()], # column and separator placed and made to stretch to the bottom of the page
]

# this is the window object with a title, reference to the layout and specified size
window = sg.Window("title",layout,size=(1050,592),element_padding=0,margins=(0,0), resizable=True)

# loop to keep the window open as long as the program is running
while True:
    # check the window for any 'events' and assign them to variables
    # continuous reading keeps the window open
    event, values = window.Read()
    # if the window is closed, exit the loop, removing the window
    # this also prevents the program from attempting to read from a closed window
    if event == sg.WIN_CLOSED:
        break

# close the window as the program ends
window.close()
