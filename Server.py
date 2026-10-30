import socket # same as client
import json # same as client
import threading # needed to allow multiple client requests to be handled at once
import pymysql # needed to handle database
from file_read_backwards import FileReadBackwards # needed to read the file backwards
import queue # needed for threading queues
from time import sleep # needed to add delays and prevent response mixing

# ▄▄▄▄▄▄                        ▄      ▀
# █      ▄   ▄  ▄ ▄▄    ▄▄▄   ▄▄█▄▄  ▄▄▄     ▄▄▄   ▄ ▄▄    ▄▄▄
# █▄▄▄▄▄ █   █  █▀  █  █▀  ▀    █      █    █▀ ▀█  █▀  █  █   ▀
# █      █   █  █   █  █        █      █    █   █  █   █   ▀▀▀▄
# █      ▀▄▄▀█  █   █  ▀█▄▄▀    ▀▄▄  ▄▄█▄▄  ▀█▄█▀  █   █  ▀▄▄▄▀



# this function will start on a new thread every time a request needs to be read and handled
# in effect this is the part of the 'server listener' that handles clients
def handle_request(conn, address):
    id_token = ""
    # create a queue for this thread
    thread_queue = queue.Queue()
    while True:
        # check for notification in queue
        try:
            print("Attemptign to get a notification...")
            print("Current state of the queue:\n" + str(thread_queue.get_nowait))
            # get the chat name from the queue flag
            chat_name = thread_queue.get_nowait()
            print("Chat name extracted from queue.")
            # prepare the notification json
            notification = json.dumps(
                {
                    "header":{
                        "id_token":id_token,
                        "chat_name":chat_name
                    },"data":{
                        "notification":"chat_updated"}
                    }
            )
            print("Notification json created")
            print("Attempting to send the notification...")
            # send the notification
            conn.sendall(notification.encode())
            print("Notification sent")
        except:
            print("Failed to find a notification.")
            pass


        # set the variable 'data' to the data received throug the connection.
        data = bytearray()
        conn_dropped = False
        # reading loop
        while True:
            packet = conn.recv(1024)
            # break out of the thread using a var if conn dropped
            if packet == b'':
                conn_dropped = True
                break
            # add packet received to data
            data.extend(packet)
            try: # check if the data is complete by trying to convert json
                temp = data.decode()
                print("Packet decoded.")
                temp = json.loads(temp)
                print("Json converted.")
                break
            except: # iterate and read again
                print("Packet unfinished")

        # terminate if connection dropped
        if conn_dropped == True:
            print("Connection dropped, attempting to kill thread...")
            break

        # convert data to a dict for processing
        data = data.decode()
        data = json.loads(data)

        # set id_token to id_token received just once
        # and also add the queue to the dict just once
        if id_token == "":
            id_token = data["header"]["id_token"]
            notification_queues[id_token] = thread_queue

        # match-case used to check what the request type is and act apropriately
        match data["header"]["request_type"]:
            case "Addition Test": # case for the test function
                # pass the data received to the function and send back the result
                conn.sendall(
                    addition(
                        data["data"]["num1"],
                        data["data"]["num2"]
                    )
                )
            case "MESSAGE": # case for the send message function
                # pass the message and chat name to the function
                conn.sendall(send_message(
                    data["data"]["message"],
                    data["header"]["chat_name"],
                    data["header"]["id_token"]
                ))
            case "UPDATEHISTORY":
                conn.sendall(receive_message(
                    data["data"]["latest_index"],
                    data["header"]["chat_name"],
                    data["header"]["id_token"]
                ))

            case _: # default case
                pass


# test function to be activated by the server listener
def addition(num1,num2):
    chat_update_notification("Test_Group")
    # calculate the total
    total = num1 + num2
    # put the total into a correctly formatted json response and convert to json string
    total = json.dumps({"header":{"id":"Test",},"data":{"total":total}})
    # return the encoded result
    return total.encode()


#function for querying data from the database
def database_request(query):
    connection = pymysql.connect( # establish tcp connection
        host="127.0.0.1", # localhost 'loopback' address
        user="MicroMessenger_Server", # username
        password="MMSPass456", # password
        database="MicroMessenger", # database to access
        port=3306,
        cursorclass=pymysql.cursors.DictCursor  # set cursor to return dictionary for record
    )

    try:
        with connection.cursor() as cursor: # use cursor object just for this connection
            cursor.execute(query) # sends query and stores the result inside the cursor object
            result = cursor.fetchall() # fetches all rows of results, returning a list of dictionaries
            return(result) # return the result
    finally:
        connection.close() # closes the connection to not overflow mariadb's limit


# function for sending client messages to chats
def send_message(message, chat_name, id_token):
    # check if token is absent from database
    if database_request(f"SELECT id_token FROM users WHERE id_token = '{id_token}';") == ():
        # send json back with error message
        return json.dumps({"error":"Error: id_token is invalid"})

    elif database_request( # uses a subquery to check if the username of the given user (through id_token) is absent from the chat
        f"SELECT * FROM memberships WHERE username = (SELECT username FROM users WHERE id_token = '{id_token}') AND chat_name = '{chat_name}';") == ():
        # send json back with error message
        return json.dumps({"error":"Error: chat is invalid"})

    # get the path of the chat history file and set to a variable
    history_file_path = database_request(f"SELECT history FROM chats WHERE chat_name = '{chat_name}';")[0]["history"].decode()

    # get the index of the latest message, use ./ to go to 'this directory' + history path
    with FileReadBackwards(f".{history_file_path}", encoding="utf-8") as file_backwards:
        # read data from the file only once and assign to a variable for re-use
        file_data = file_backwards.readline()
        # check if the file is empty
        if file_data == "":
            latest_index = tuple([0]) # set latest index to zero (so first message will be 1)
        else:
            # read the last line, load it from a json to dict, get the key from the object
            # which will be the index
            latest_index = json.loads(file_data).keys()

    # calculate the new_index by incrementing
    # the error here is superficial, the code is actually good
    new_index = int(list(latest_index)[0]) + 1

    # get the username of the user and assign it to a variable
    username = database_request(f"SELECT username FROM users WHERE id_token = '{id_token}';")[0]["username"].decode()
    # construct a complete json string using the message and assign to a new variable to be the complete message object
    message = json.dumps({str(new_index):[username, message]})

    # append the message object to the chat history file
    with open(f".{history_file_path}","a") as chat_file:
        chat_file.write("\n" + message)

    # trigger a function to send out a chat update notification
    chat_update_notification(chat_name)

    # wait so that the responses don't mix
    sleep(1.0)

    # send a confirmation to the server
    return json.dumps({"confirmation":True}).encode()


# send update notification to all users in a chat
def chat_update_notification(chat_name):
    print("Attempting to send chat update notification...")
    # get usernames of all members of the chat
    members = database_request(f"SELECT username FROM memberships WHERE chat_name = '{chat_name}';")
    # iterate through each of the json obects that corresponds to a username
    for user in members:
        print("Extracting username of a member...")
        # get the username out of the json object, decode to string
        username = user["username"].decode()
        # for this user, fetch the IP address and id token
        id_token = database_request(f"SELECT id_token FROM users WHERE username = '{username}';")[0]["id_token"].decode()
        try:
            print("Attempting to put notification in queue...")
            # get the queue of the thread that handles the client which needs a notification
            thread_queue = notification_queues[id_token]
            # put a flag in the queue
            thread_queue.put(chat_name)
            print("Notification successfully placed in queue.")
        except:
            print("Failed to put notification in queue.")
            pass
    print("Chat update thread closing...")

def receive_message(latest_index, chat_name, id_token):
    # check for errors
    if database_request(f"SELECT id_token FROM users WHERE id_token = '{id_token}';") == ():
        # send json back with error message
        return json.dumps({"error":"Error: id_token is invalid"})

    elif database_request( # uses a subquery to check if the username of the given user (through id_token) is absent from the chat
        f"SELECT * FROM memberships WHERE username = (SELECT username FROM users WHERE id_token = '{id_token}') AND chat_name = '{chat_name}';") == ():
        # send json back with error message
        return json.dumps({"error":"Error: chat is invalid"})

    # create the reponse to later add messages to it
    response = {
        "header":{
            "id_token":id_token,
            "chat_name":chat_name
        },"data":{
            # messages will go in here
        }, "error":"None"
    }

    # get the file path of the chat
    history_file_path = database_request(f"SELECT history FROM chats WHERE chat_name = '{chat_name}';")[0]["history"].decode()

    # get the index of the latest message, use ./ to go to 'this directory' + history path
    with FileReadBackwards(f".{history_file_path}", encoding="utf-8") as file_backwards:
        # read data from the file only once and assign to a variable for re-use
        for line in file_backwards:
            print("The value read is: " + line)
            try:
                message = json.loads(line)
            except:
                print("Failed to read a message to send back: " + line) # log
                break
            # get the index of the message read and compare it to latest_index
            if int(list(message.keys())[0]) > int(latest_index):
                # run if above latest index
                # add message to data section
                response["data"].update(message)
            else:
                print("Passed latest index: " + str(list(message.keys())[0]))
                # if latest index is reached, stop reading
                break
    print("The message response to be sent to the client is:", response)
    # send the messages back to the client
    return json.dumps(response).encode()



# ▄▄▄▄▄                                                    ▄▄▄▄    ▄                    ▄
# █   ▀█  ▄ ▄▄   ▄▄▄    ▄▄▄▄   ▄ ▄▄   ▄▄▄   ▄▄▄▄▄         █▀   ▀ ▄▄█▄▄   ▄▄▄    ▄ ▄▄  ▄▄█▄▄
# █▄▄▄█▀  █▀  ▀ █▀ ▀█  █▀ ▀█   █▀  ▀ ▀   █  █ █ █         ▀█▄▄▄    █    ▀   █   █▀  ▀   █
# █       █     █   █  █   █   █     ▄▀▀▀█  █ █ █             ▀█   █    ▄▀▀▀█   █       █
# █       █     ▀█▄█▀  ▀█▄▀█   █     ▀▄▄▀█  █ █ █         ▀▄▄▄█▀   ▀▄▄  ▀▄▄▀█   █       ▀▄▄
#                       ▄  █
#                        ▀▀



# dict holding queues for client threads
notification_queues = {}

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
