#!/usr/bin/env python
# ./ncbot.py <hostname>:<port> <nick> <secret>

# example:
# ./ncbot csx1:12345 bot1 green

# to start ncat broker:
# nc --broker -l 12345

#implements the ncbot to connect to a Ncat broker server.



import argparse
import socket
import sys
import os
#import base64
import hashlib
import shlex
import time
from array import *
from typing import Union

#global nonce
seen_nonces = list()

# Count of commands seen and executed
commands_exe = 0    #maybe change so its not global

# Argument Parsing
def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname_port', help='hostname and port of the server')
    parser.add_argument('nickname', help='bot nickname')
    parser.add_argument('secret', help='bot secret')
    return parser.parse_args()

# Implementing the status command for all bots
def status_cmd(sock: socket, nick: str):
    global commands_exe
    status_send = "-status " + nick + " " + str(commands_exe) + "\n"
    sock.send(status_send.encode())
    commands_exe += 1

# Implementing the shutdown command for all bots
def shutdown_cmd(sock: socket, nick: str):
    shutdown_send = "-shutdown " + nick  + "\n"
    sock.send(shutdown_send.encode())
    sock.close()
    print("I have shutdown")
    exit(1)

# Implements the command that allows bots to send an attack message to a server
def attack_server(sock: socket, hostname: str, port: int, nickname: str, nonce: str):
    try:
        # Connect to server being attacked
        attack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attack_socket.connect((hostname, port))
        
        # Construct attack
        attack_send = nickname + nonce
        
        try:
            # Attack the server
            attack_socket.send(attack_send.encode())
            
        except Exception as error:
            # Attack error
            failNoSend = "-attack " + nickname + " FAIL Could not send attack : " + str(error)
            sock.send(failNoSend.encode())
            print(failNoSend)
            return
    # Could not connect to attack server
    except Exception as error:
        print("-attack ", nickname, " FAIL ", error)
        return

    # Close attack socket and notify controller of attack
    attack_socket.close()
    attackOK = "-attack " + nickname + " OK"
    sock.send(attackOK.encode())
    print(attackOK)
    
    # Increase command count
    commands_exe += 1
    return

def move_server(host:str, port:int, args:str):
 while(1):
        try:
            # Connect to specified server
            new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_client_socket.connect((host, port))
            
             # Sends initial join message to server
            sendNickname = "-joined " + args.nickname
            
            # Repeat the initial join message to the new server
            new_client_socket.send(sendNickname.encode())

            print("Connected.")

        except ConnectionError:
            # Failed to move to new server
            print("Failed to connect.")
            time.sleep(5)

        # If successful connection, run the bot on the new server
        while(1):
            try:
                client_program(args, new_client_socket)
            
            # Lost connection to the server
            except ConnectionError:
                print("lost connection.")
    # Increase command count            
    commands_exe += 1
def client_program(args: str, sock: socket):
    # Split the host and port into separate variables (Ex : csx1:2025)
    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])

    # Receive the command that the controller has given to the bot
    command = sock.recv(1024).decode()

    
    cmd_data = command.split()
    global commands_exe
    # Authenticate the command:
    if cmd_data[0] in seen_nonces:
        # Ignore command
        print("nonce seen")
    else:
        # Generate MAC to verify command
        mac2 = str(hashlib.sha256((cmd_data[0] + args.secret).encode('utf-8')).hexdigest())
        mac2_short = mac2[0:8]
        
        # MAC matches
        if mac2_short == str(cmd_data[1]):
            seen_nonces.append(cmd_data[0])
            #execute command
            
            # If status command is received
            if cmd_data[2] == "status":
                status_cmd(sock, args.nickname)
                
            # If shutdown command is received
            elif cmd_data[2] == "shutdown":
                print("telling bot to shutdown")
                shutdown_cmd(sock, args.nickname)
                
            # If attack command is received
            elif cmd_data[2] == "attack":
                split_attack = cmd_data[3].split(":")
                print(int(split_attack[1]))
                attack_server(sock, split_attack[0], int(split_attack[1]), args.nickname, cmd_data[0])
                
            # If move command is received
            elif cmd_data[2] == "move":
                moveBot = "-move " + args.nickname
                print(moveBot)
                sock.send(moveBot.encode())
                split_move = cmd_data[3].split(":")
                sock.close()
                move_server(split_move[0], int(split_move[1]), args)


def main():
    args = parse_args()
    while(1):
        try:
            #initially connect to server
            split_hostPort = args.hostname_port.split(":")
            host = split_hostPort[0]
            port = int(split_hostPort[1])
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
             #sends initial join message to server
            sendNickname = "-joined " + args.nickname

            client_socket.send(sendNickname.encode())

            print("Connected.")

        except ConnectionError:
            #print("Connection failed. Is the server dead?")
            print("Failed to connect.")
            time.sleep(5)

        while(1):
            try:
                client_program(args, client_socket)

            except ConnectionError:
                print("lost connection.")




if __name__ == '__main__':
    main()