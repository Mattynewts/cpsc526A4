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
commands_exe = 0    #maybe change so its not global

def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname_port', help='hostname and port of the server')
    #parser.add_argument('port', type=int, help='port where server listens')
    parser.add_argument('nickname', help='bot nickname')
    parser.add_argument('secret', help='bot secret')
    #parser.add_argument('-d', '--debug', action='store_true',
    #                    help="enable debugging output")
    return parser.parse_args()


def status_cmd(sock: socket, nick: str):
    global commands_exe
    status_send = "-status " + nick + " " + str(commands_exe) + "\n"
    sock.send(status_send.encode())
    commands_exe += 1
    #implement status command


def shutdown_cmd(sock: socket, nick: str):
    shutdown_send = "-shutdown " + nick  + "\n"
    sock.send(shutdown_send.encode())
    #sock.flush()
    sock.close()
    print("I have shutdown")
    exit(1)



def attack_server(sock: socket, hostname: str, port: int, nickname: str, nonce: str):
    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.connect((hostname, port))
    #attack_send = nickname + nonce
    try:
        attack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attack_socket.connect((hostname, port))
        attack_send = nickname + nonce
        attack_socket.send(attack_send.encode())
        try:
            attack_socket.send(attack_send.encode())
        except:
            failNoSend = "-attack " + nickname + " FAIL Could not send attack"
            sock.send(failNoSend.encode())
            print(failNoSend)
            return

    except Exception as error:
        failError = "-attack " + nickname + " FAIL " + str(error)
        sock.send(failError.encode())
        print(failError)
        return

    attack_socket.close()
    attackOK = "-attack " + nickname + " OK"
    sock.send(attackOK.encode())
    print(attackOK)
    return

def move_server(host:str, port:int, args:str):
 while(1):
        try:
            #initially connect to server
            new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_client_socket.connect((host, port))
             #sends initial join message to server
            sendNickname = "-joined " + args.nickname

            new_client_socket.send(sendNickname.encode())

            print("Connected.")

        except ConnectionError:
            #print("Connection failed. Is the server dead?")
            print("Failed to connect.")
            time.sleep(5)

        while(1):
            try:
                client_program(args, new_client_socket)

            except ConnectionError:
                print("lost connection.")

def client_program(args: str, sock: socket):

    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])


    command = sock.recv(1024).decode()
    #print("Recieved from server: ", command)

    cmd_data = command.split()
    global commands_exe
    #authenticate the command:
    if cmd_data[0] in seen_nonces:
        #ignore command
        print("nonce seen")
    else:
        mac2 = str(hashlib.sha256((cmd_data[0] + args.secret).encode('utf-8')).hexdigest())
        mac2_short = mac2[0:8]
        #print("mac2: ", mac2_short)
        if mac2_short == str(cmd_data[1]):
            #ignore comand
            #print("macs do not match")
            seen_nonces.append(cmd_data[0])
            #execute command
            if cmd_data[2] == "status":
                status_cmd(sock, args.nickname)
                #commands_exe += 1
            elif cmd_data[2] == "shutdown":
                print("telling bot to shutdown")
                shutdown_cmd(sock, args.nickname)
                #implement shutdown bot
                #commands_exe += 1
            elif cmd_data[2] == "attack":
                split_attack = cmd_data[3].split(":")
                print(int(split_attack[1]))
                attack_server(sock, split_attack[0], int(split_attack[1]), args.nickname, cmd_data[0])
                commands_exe += 1
            elif cmd_data[2] == "move":
                moveBot = "-move " + args.nickname
                print(moveBot)
                sock.send(moveBot.encode())
                split_move = cmd_data[3].split(":")
                sock.close()
                move_server(split_move[0], int(split_move[1]), args)
                commands_exe += 1
            #print("command authenticated")
        #else we ignore comand
            #print("macs do not match")


        #client_socket.send(message.encode)
        #client_socket.close()
    #except:
       #print("Disconnected.")
        #continue


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
            while(1):
                try:
                    client_program(args, client_socket)

                except ConnectionError:
                    print("lost connection.")

        except ConnectionError:
            #print("Connection failed. Is the server dead?")
            print("Failed to connect.")
            time.sleep(5)




if __name__ == '__main__':
    main()