import socket # needed for using sockets for networking
import json # needed to convert dicts to json form
            # (this is useful since it can convert variables to their values in the json string)
import PySimpleGUI as sg # needed for the GUI; abbreviated for ease of use
'ASCII comment titles generated with https://patorjk.com/software/taag/#p=display&f=Mono+9&t=Functions&x=none&v=4&h=4&w=80&we=false using font "Mono 9"'


# IP of server and port for access

HOST = "127.0.0.1"
PORT = 65432




# ▄▄▄▄▄▄                        ▄      ▀
# █      ▄   ▄  ▄ ▄▄    ▄▄▄   ▄▄█▄▄  ▄▄▄     ▄▄▄   ▄ ▄▄    ▄▄▄
# █▄▄▄▄▄ █   █  █▀  █  █▀  ▀    █      █    █▀ ▀█  █▀  █  █   ▀
# █      █   █  █   █  █        █      █    █   █  █   █   ▀▀▀▄
# █      ▀▄▄▀█  █   █  ▀█▄▄▀    ▀▄▄  ▄▄█▄▄  ▀█▄█▀  █   █  ▀▄▄▄▀



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


# function to send messages from input to the server
def send_message(message, current_chat): # message to send + chat to send to
    if validate_input(message,"message") == True:
        request = { # request JSON dict
            "header":{
                "id":"Test",
                "request_type":"MESSAGE", # appropriate type
                "chat_name":current_chat # destination must be included
            },
            "data":{
                "message":message # payload
            }
        }
        request = json.dumps(request)
        send_request(request)


def validate_input(input_text, input_type):
    match input_type: # check which type of input is given
        case "message": # case for message inputs
            if len(input_text) > 1000 or len(input_text) < 1: # len check
                sg.popup("Message input is invalid") # create a error popup
                return False # return false to whatever called for validation
            else:
                return True # return true to whatever called for validation
        case _ : pass # if input_type is wrong, just give up



# ▄                                    ▄
# █       ▄▄▄   ▄   ▄   ▄▄▄   ▄   ▄  ▄▄█▄▄   ▄▄▄
# █      ▀   █  ▀▄ ▄▀  █▀ ▀█  █   █    █    █   ▀
# █      ▄▀▀▀█   █▄█   █   █  █   █    █     ▀▀▀▄
# █▄▄▄▄▄ ▀▄▄▀█   ▀█    ▀█▄█▀  ▀▄▄▀█    ▀▄▄  ▀▄▄▄▀
#                ▄▀
#               ▀▀



# direct chat left column, for selecting direct chats and also page switches
dc_column_left = [
    [sg.Button("Group Chats Page", font=(None,25))], # title text element
    [sg.Button("Test Chat",auto_size_button=False,font=(None,20),expand_x=True)] # button to represent chat selection
]


# direct chat right column, for reading and sending messages
dc_column_right = [
    [sg.Text("Test Username",expand_x=True,font=(None,40))], # title
    [sg.HorizontalSeparator()], # horizontal line
    [sg.Output(wrap_lines=True,expand_x=True,expand_y=True)], # chat output area - text wrapping enabled
    [sg.Multiline(wrap_lines=True,expand_x=True,size=(None,3)),sg.Button("Send",font=(None,20))] # input box
]


# this array will hold all of the elements for the direct chat window
dc_layout =[
    [
        sg.Column(
            dc_column_left, # use the left hand column layout
            key=("-DC_LEFT-"), # set the key for repacking
            expand_y=True, # expand to fill vertical space
            scrollable=True, # make the column scroallable
            vertical_scroll_only=True, # leave only the vertical scroll bar
            expand_x=True), # expand to fill horizontal space
        sg.VerticalSeparator(), # separator between left and right
        sg.Column(
            dc_column_right, # use the right hand column layout
            key=("-DC_RIGHT-"), # set the key for repacking
            expand_y=True, # expand to fill vertical space
            expand_x=True), # expand to fill horizontal space
    ],
]

# group chat left column, for selecting group chats and also page switches
gc_column_left = [
    [sg.Button("Direct Chats Page", font=(None,25))], # title text element
    [sg.Button("Test Group",auto_size_button=False,font=(None,20),expand_x=True)] # button to represent chat selection
]


# group chat right column, for reading and sending messages
gc_column_right = [
    [sg.Text("Test Group Chat Name",expand_x=True,font=(None,40))], # title
    [sg.HorizontalSeparator()], # horizontal line
    [sg.Output(wrap_lines=True,expand_x=True,expand_y=True)], # chat output area - text wrapping enabled
    [sg.Multiline(wrap_lines=True,expand_x=True,size=(None,3)),sg.Button("Send",font=(None,20))] # input box
]


gc_layout = [
    [
        sg.Column(
            gc_column_left, # use the left hand column layout
            key=("-GC_LEFT-"), # set the key for repacking
            expand_y=True, # expand to fill vertical space
            scrollable=True, # make the column scroallable
            vertical_scroll_only=True, # leave only the vertical scroll bar
            expand_x=True # expand to fill horizontal space
        ),
        sg.VerticalSeparator(), # separator between left and right
        sg.Column(
            gc_column_right, # use the right hand column layout
            key=("-GC_RIGHT-"), # set the key for repacking
            expand_y=True, # expand to fill vertical space
            expand_x=True # expand to fill horizontal space
        ),
    ],
]

# make the one layout for the whole window
frames = [
    [sg.Column(
        #title="", # no frame title, saves space
        layout=dc_layout, # this frame holds DC
        expand_x=True, # fill whole screen
        expand_y=True, # fill whole screen
        key="-DC_FRAME-" # key
    ),
    sg.Column(
        #title="", # no frame title, saves space
        layout=gc_layout, # this frame holds GC
        expand_x=True, # fill whole screen
        expand_y=True, # fill whole screen
        key="-GC_FRAME-", # key
        visible=False
    )]
]

main_layout = [[sg.Column(frames,expand_x=True,expand_y=True)]] # main layout



# ▄▄▄▄▄                                                    ▄▄▄▄    ▄                    ▄
# █   ▀█  ▄ ▄▄   ▄▄▄    ▄▄▄▄   ▄ ▄▄   ▄▄▄   ▄▄▄▄▄         █▀   ▀ ▄▄█▄▄   ▄▄▄    ▄ ▄▄  ▄▄█▄▄
# █▄▄▄█▀  █▀  ▀ █▀ ▀█  █▀ ▀█   █▀  ▀ ▀   █  █ █ █         ▀█▄▄▄    █    ▀   █   █▀  ▀   █
# █       █     █   █  █   █   █     ▄▀▀▀█  █ █ █             ▀█   █    ▄▀▀▀█   █       █
# █       █     ▀█▄█▀  ▀█▄▀█   █     ▀▄▄▀█  █ █ █         ▀▄▄▄█▀   ▀▄▄  ▀▄▄▀█   █       ▀▄▄



# create the window
window = sg.Window(
    "Direct Chats", # title of the window
    main_layout, # layout containing different frames
    size=(1050,592), # set the initial size
    element_padding=0, # padding to zero to save space
    margins=(0,0), # elements
    resizable=True, # window can be resized
    finalize=True # finalise to be able to access widgets
)

# set variables to dc widgets extracted from column elements using keys
column_left, column_right = window["-DC_LEFT-"].widget, window["-DC_RIGHT-"].widget
# use the repack function to pack the left column properly before the right
repack(column_left,{'fill':'y', 'expand':0, 'before':column_right})

# set variables to gc widgets extracted from column elements using keys
column_left, column_right = window["-GC_LEFT-"].widget, window["-GC_RIGHT-"].widget
# use the repack function to pack the left column properly before the right
repack(column_left,{'fill':'y', 'expand':0, 'before':column_right})

# loop to keep the window open as long as the program is running
while True:
    # check the window for any 'events' and assign them to variables
    # continuous reading keeps the window open
    event, values = window.Read()

    # block to do things based on events
    if event == sg.WIN_CLOSED:
        # if the window is closed, exit the loop, removing the window
        # this also prevents the program from attempting to read from a closed window
        break
    elif event == "Group Chats Page": # change page from dc to gc
        window["-GC_FRAME-"].update(visible=True) # reveal the gc frame
        window["-DC_FRAME-"].update(visible=False) # hide the dc frame#


    elif event == "Direct Chats Page": # change page from gc to dc
        window["-DC_FRAME-"].update(visible=True) # reveal the dc frame
        window["-GC_FRAME-"].update(visible=False) # hide the gc frame

# close the window as the program ends
window.close()
