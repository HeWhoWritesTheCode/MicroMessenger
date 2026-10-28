import socket # needed for using sockets for networking
import json # needed to convert dicts to json form
            # (this is useful since it can convert variables to their values in the json string)
import PySimpleGUI as sg # needed for the GUI; abbreviated for ease of use
import threading # for listening for server notifications
import queue # queue for notifications
from file_read_backwards import FileReadBackwards # needed to read the file backwards
'ASCII comment titles generated with https://patorjk.com/software/taag/#p=display&f=Mono+9&t=Functions&x=none&v=4&h=4&w=80&we=false using font "Mono 9"'


# IP of server and port for access
HOST = "127.0.0.1"
PORT = 65432
# id_token for this Client program
id_token = "Test_User_1"


# ▄▄▄▄▄▄                        ▄      ▀
# █      ▄   ▄  ▄ ▄▄    ▄▄▄   ▄▄█▄▄  ▄▄▄     ▄▄▄   ▄ ▄▄    ▄▄▄
# █▄▄▄▄▄ █   █  █▀  █  █▀  ▀    █      █    █▀ ▀█  █▀  █  █   ▀
# █      █   █  █   █  █        █      █    █   █  █   █   ▀▀▀▄
# █      ▀▄▄▀█  █   █  ▀█▄▄▀    ▀▄▄  ▄▄█▄▄  ▀█▄█▀  █   █  ▀▄▄▄▀



# function to re-pack the columns, taking a Tkinter widget and the options
def repack(widget, option):
    # set variable to packing info of the widget
    pack_info = widget.pack_info()
    # update the packing info
    pack_info.update(option)
    # re-pack the widget
    widget.pack(pack_info)


#function for sending requests to the server
def send_request(data):
    # send the specified data as UTF-8 binary to the server
    sock.sendall(data.encode())
    # try and receive data (if any)
    try:
        # receive data
        return_data = sock.recv(1024)
        # return the data
        return return_data
    except:
        pass


# test function for carrying out 2+2
def test_function():
    # create a dictionary to hold the json request with test data and instructions
    request = {"header":{"id_token":id_token,"request_type":"Addition Test"},"data":{"num1":2, "num2":2}}
    # convert the dictionary to a json-form string
    request = json.dumps(request)
    # pass the json to the send_request function so that the request will be sent to the server
    response = send_request(request, None)
    # decode the response bytes
    response.decode()
    # convert the json into a dictionary so data can be accessed more easily
    response = json.loads(response)
    # return the data stored in the json response
    return response["data"]["total"]


def validate_input(input_text, input_type):
    match input_type: # check which type of input is given
        case "message": # case for message inputs
            if isinstance(input_text,str) == False: # check for wrong type
                sg.popup("Message input is invalid") # create a error popup
                return False # return false to whatever called for validation
            if len(input_text) > 1000 or len(input_text) < 1: # len check
                sg.popup("Message input is invalid") # create a error popup
                return False # return false to whatever called for validation
            else:
                return True # return true to whatever called for validation
        case _ : pass # if input_type is wrong, just give up


# function to send messages from input to the server
def send_message(message, current_chat): # message to send + chat to send to
    if validate_input(message,"message") == True:
        request = { # request JSON dict
            "header":{
                "id_token":id_token,
                "request_type":"MESSAGE", # appropriate type
                "chat_name":current_chat # destination must be included
            },
            "data":{
                "message":message # payload
            }
        }
        request = json.dumps(request)
        try:
            # send the given request
            response = send_request(request)
            # convert the json from binary to a dict
            response.decode()
            response = json.loads(response)
            # check that there is an error in the response
            if response["error"] != "None":
                # produce a popup if there is an error
                sg.popup(response["error"])
            elif response["confirmation"] != True:
                sg.popup("Messge failed to send. Connection err.")
        except:
            pass


# update a given chat (i.e receive a message)
def update_chat(chat_name):
    with FileReadBackwards(f"./Message_Histories/{chat_name}.jsonl", encoding="utf-8") as file_backwards:
        # read data from the file only once and assign to a variable for re-use
        file_data = file_backwards.readline()
        # check if the file is empty
        if file_data == "":
            latest_index = 0 # set latest index to zero (so next message will be 1)
        else:
            # read the last line, load it from a json to dict, get the key from the object
            # which will be the index
            latest_index = json.loads(file_data).keys()
            # convert the dict_key to an int
            latest_index = int(list(latest_index)[0])

    request = { # request JSON dict
        "header":{
            "id_token":id_token,
            "request_type":"UPDATEHISTORY", # appropriate type
            "chat_name":chat_name # destination must be included
        },
        "data":{
            "latest_index":str(latest_index)
        }
    }
    # send the request
    request = json.dumps(request)
    # receive and decode the response
    sg.Print("Attempting to send update request", do_not_reroute_stdout=True)
    response = send_request(request)
    sg.Print("Update response received: " + str(response), do_not_reroute_stdout=True)
    response.decode()
    sg.Print("Response decoded.", do_not_reroute_stdout=True)
    response = json.loads(response)
    sg.Print("Response converted from json.", do_not_reroute_stdout=True)
    # check that there is an error in the response
    if response["error"] != "None":
        sg.Print("Error found in update response, attempting popup...", do_not_reroute_stdout=True)
        # produce a popup if there is an error
        sg.popup(response["error"])
    # check for confirmation
    elif response["confirmation"] == True:
        sg.Print("No error, continuing...", do_not_reroute_stdout=True)
        # get all the messages from the data object
        messages = response["data"]
        sg.Print("Messages extracted.", do_not_reroute_stdout=True)
        # write to the chat history file
        with open(f"./Message_Histories/{chat_name}.jsonl", "a") as chat_file:
            sg.Print("History file opened.", do_not_reroute_stdout=True)
            # iterate over all the message
            for index, payload in messages:
                sg.Print("Reading through messages...", do_not_reroute_stdout=True)
                # construct the json object to append
                message = json.dumps({index:payload})
                sg.Print("Message formatted.", do_not_reroute_stdout=True)
                chat_file.write("\n" + message)
                sg.Print("Written " + message + " to file.", do_not_reroute_stdout=True)
        update_chat_gui(latest_index, chat_name)


def notification_listener():
    while True:
        # accept data
        data = sock.recv(2024)
        sg.Print("Notification received...", do_not_reroute_stdout=True)
        # extract chat_name from json
        chat_name = json.loads(data.decode())["header"]["chat_name"]
        sg.Print("Chat name extracted from notification: " + chat_name, do_not_reroute_stdout=True)
        # add the notification to the queue to be picked up
        notifications.put(chat_name)
        sg.Print("Notification placed in queue", do_not_reroute_stdout=True)


def update_chat_gui(latest_index, chat_name):
    sg.Print("The gui update function has run...", do_not_reroute_stdout=True)
    msg_stack = [] # stack for reversal
    # read the correct chat history file backwards
    with FileReadBackwards(f"./Message_Histories/{chat_name}.jsonl", encoding="utf-8") as file_backwards:
        sg.Print("File opened...", do_not_reroute_stdout=True)
        # read data from the file only once and assign to a variable for re-use
        for line in file_backwards:
            sg.Print("Iterating through file...", do_not_reroute_stdout=True)
            # convert the dict key type to get an int
            try:
                index = int(list(json.loads(line).keys())[0])
            except:
                pass
            sg.Print("Set an index for a message.", do_not_reroute_stdout=True)
            if index > latest_index:
                try:
                    sg.Print("Attempting to get payload from the message...", do_not_reroute_stdout=True)
                    # extract the array from the message json & append
                    msg_stack.append(json.loads(line)[str(index)])
                    sg.Print("Successfully read the message.", do_not_reroute_stdout=True)
                except:
                    sg.Print("Failed to read the message.", do_not_reroute_stdout=True)
                    break # blank line read, so just ignore and stop reading
        for i in range(len(msg_stack)):
            sg.Print("Attempting to output the messages...", do_not_reroute_stdout=True)
            # get the message payload array from the stack
            text = msg_stack.pop()
            sg.Print("Message retrieved from stack.", do_not_reroute_stdout=True)
            text = text[0] + ">> " + text[1] # format the message
            sg.Print("Message text formatted", do_not_reroute_stdout=True)
            window[f"-OUT_{chat_name}-"].update(text + "\n", append=True)
            sg.Print("Message output!", do_not_reroute_stdout=True)



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
    [sg.Multiline(wrap_lines=True,expand_x=True,expand_y=True, disabled=True, write_only=True)], # chat output area - text wrapping enabled
    [sg.Multiline(wrap_lines=True,expand_x=True,size=(None,3)),sg.Button("Send",key="-SEND_MESSAGE2-",font=(None,20))] # input box
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
    [sg.Multiline(key="-OUT_Test_Group-", wrap_lines=True,expand_x=True,expand_y=True, disabled=True, write_only=True)], # chat output area - text wrapping enabled
    [sg.Multiline(key="-TEST_GROUP_INPUT-",wrap_lines=True,expand_x=True,size=(None,3)),sg.Button("Send",key="-SEND_MESSAGE1-",font=(None,20))] # input box
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
#                       ▄  █
#                        ▀▀



# create a socket using IPv4 and TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the server (localhost currently for development)
sock.connect((HOST,PORT))

# make a queue to hold incoming notifications
notifications = queue.Queue()
notification_listener_thread = threading.Thread(target=notification_listener, name="notifications", args=())
notification_listener_thread.start()



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

# output all messages for the test group
# in future, this will be will be for all groups
update_chat_gui(0,"Test_Group")

# loop to keep the window open as long as the program is running
while True:
    # check for notifications
    try:
        notification = notifications.get_nowait()
        update_chat(notification)
    except:
        pass

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
        window["-DC_FRAME-"].update(visible=False) # hide the dc frame

    elif event == "Direct Chats Page": # change page from gc to dc
        window["-DC_FRAME-"].update(visible=True) # reveal the dc frame
        window["-GC_FRAME-"].update(visible=False) # hide the gc frame

    elif event.startswith("-SEND_MESSAGE"): # send a message
        # use values dict to get message and send the message
        send_message(values["-TEST_GROUP_INPUT-"],"Test_Group")

# close the window as the program ends
window.close()
sock.close()
