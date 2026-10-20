import socket # same as client
import json # same as client
import threading # needed to allow multiple client requests to be handled at once
import pymysql # needed to handle database
from file_read_backwards import FileReadBackwards



# ▄▄▄▄▄▄                        ▄      ▀
# █      ▄   ▄  ▄ ▄▄    ▄▄▄   ▄▄█▄▄  ▄▄▄     ▄▄▄   ▄ ▄▄    ▄▄▄
# █▄▄▄▄▄ █   █  █▀  █  █▀  ▀    █      █    █▀ ▀█  █▀  █  █   ▀
# █      █   █  █   █  █        █      █    █   █  █   █   ▀▀▀▄
# █      ▀▄▄▀█  █   █  ▀█▄▄▀    ▀▄▄  ▄▄█▄▄  ▀█▄█▀  █   █  ▀▄▄▄▀



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
        case "Addition Test": # case for the test function
            # pass the data received to the function and send back the result
            conn.sendall(
                addition(
                    data["data"]["num1"],
                    data["data"]["num2"]
                )
            )
        case "MESSAGE": # case for send message function
            # pass the message and chat name to the function and send the result back
            conn.sendall(
                message(
                    data["data"]["message"],
                    data["header"]["chat_name"],
                    data["header"]["id"]
                )
            )
        case _: # default case
            pass

# test function to be activated by the server listener
def addition(num1,num2):
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
def message(message, chat_name, id_token):
    # check if token is absent from database
    if database_request(f"SELECT id_token FROM users WHERE id_token = '{id_token}';") == ():
        # send json back with error message
        return json.dumps({"data":{"error":"Error: id_token is invalid"}})

    elif database_request( # uses a subquery to check if the username of the given user (through id_token) is absent from the chat
        f"SELECT * FROM memberships WHERE username = (SELECT username FROM users WHERE id_token = '{id_token}') AND chat_name = '{chat_name}';") == ():
        # send json back with error message
        return json.dumps({"data":{"error":"Error: chat is invalid"}})

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

def chat_update_notification(chat_name):
    members = database_request(f"SELECT * FROM memberships WHERE chat_name = '{chat_name}';")



# ▄▄▄▄▄                                                    ▄▄▄▄    ▄                    ▄
# █   ▀█  ▄ ▄▄   ▄▄▄    ▄▄▄▄   ▄ ▄▄   ▄▄▄   ▄▄▄▄▄         █▀   ▀ ▄▄█▄▄   ▄▄▄    ▄ ▄▄  ▄▄█▄▄
# █▄▄▄█▀  █▀  ▀ █▀ ▀█  █▀ ▀█   █▀  ▀ ▀   █  █ █ █         ▀█▄▄▄    █    ▀   █   █▀  ▀   █
# █       █     █   █  █   █   █     ▄▀▀▀█  █ █ █             ▀█   █    ▄▀▀▀█   █       █
# █       █     ▀█▄█▀  ▀█▄▀█   █     ▀▄▄▀█  █ █ █         ▀▄▄▄█▀   ▀▄▄  ▀▄▄▀█   █       ▀▄▄
#                       ▄  █
#                        ▀▀



# create a new socket called 'sock'. AF_INET specifies that the socket will use the IPv4 family.
# SOCK_STREAM specifies TCP connections.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to the correct address and port.
sock.bind(("127.0.0.1", 65432))
# enable the server to accpet connections from clients.
# The int 3 specifies the backlog - which I mentioned as a buffer that will hold many requests coming in at once
sock.listen(3)

chat_update_notification("Test_Group")

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
