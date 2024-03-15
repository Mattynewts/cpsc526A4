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


def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname', help='hostname of the server')
    parser.add_argument('port', type=int, help='port where server listens')
    parser.add_argument('nickname', help='bot nickname')
    parser.add_argument('secret', help='bot secret')
    #parser.add_argument('-d', '--debug', action='store_true',
    #                    help="enable debugging output")
    return parser.parse_args()

def client_program(args: str):
    host = '127.0.0.1'
    port = 5005

    print("hostname: ", args.hostname)
    print("port: ", args.port)
    print("nickname: ", args.nickname)
    print("secret: ", args.secret)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.hostname, args.port))

    message = input('->')
    while (message.lower().strip() != 'close'):
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        print(f'Response from server {data}')

        message = input('->')
    client_socket.send(message.encode)
    client_socket.close()


def main():
    args = parse_args()
    #dbg.enabled = args.debug
    #secret = get_secret()
    print(f"connecting to {args.hostname}:{args.port} with {args.secret}")
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect((args.hostname, args.port))
    #dbg(f"connected")
    #lsock = LineSocket(sock)
    try:
        client_program(args)
        while True:
            print("wow")
            #cmd = input(">").strip()
            #handle_command(lsock, cmd)

    except ConnectionError:
        print("Connection failed. Is the server dead?")


if __name__ == '__main__':
    main()