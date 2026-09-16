import socket # needed for using sockets for networking
import json # needed to convert dicts to json form
            # (this is useful since it can convert variables to their values in the json string)
import PySimpleGUI as sg# needed for the GUI; abbreviated for ease of use

HOST = "127.0.0.1"
PORT = 65432

# function to re-pack the columns, taking a Tkinter 'widget' and the options
def repack(widget, option):
    # set variable to packing info of the widget
    pack_info = widget.pack_info()
    # update the packing info
    pack_info.update(option)
    # re-pack the widget
    widget.pack(**pack_info)

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

# direct chat left column, for selecting direct chats and also page switches
dc_column_left = [
    [sg.Text("Chats",font=(None,25),auto_size_text=False)], # title text element
    [sg.Button("Test Chat",auto_size_button=False,font=(None,20),expand_x=True)] # button to represent chat selection
]

# direct chat right column, for reading and sending messages
dc_column_right = [
    [sg.Text("Test Username",expand_x=True,font=(None,40))], # title
    [sg.HorizontalSeparator()], # horizontal line
    [sg.Output(wrap_lines=True,expand_x=True,expand_y=True)], # chat output area - text wrapping enabled
    [sg.Multiline(wrap_lines=True,expand_x=True,size=(None,3)),sg.Button("Send",font=(None,20))] # input box
]


# this array will hold all of the elements for the window
layout =[
    [
        sg.Column(dc_column_left,key=("-LEFT-"),expand_y=True,scrollable=True,vertical_scroll_only=True,expand_x=True), # left hand column, made scrollable, expands vertically
        sg.VerticalSeparator(), # separator between left and right
        sg.Column(dc_column_right,key=("-RIGHT-"),expand_y=True,expand_x=True), #right hand column, expands vertically
    ],
]

# this is the window object with a title, reference to the layout and specified size
window = sg.Window(
    "title",
    layout,size=(1050,592),
    element_padding=0,margins=(0,0),
    resizable=True,
    finalize=True # finalise to be able to access widgets
)

# set variables to widgets extracted from column elements using keys
column_left, column_right = window["-LEFT-"].widget, window["-RIGHT-"].widget
# use the repack function to pack the left column properly before the right
repack(column_left,{'fill':'y', 'expand':0, 'before':column_right})

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
