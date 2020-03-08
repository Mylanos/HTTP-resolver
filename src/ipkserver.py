#!/usr/bin/env python3

##################################################
 # Soubor: ipkserver.py
 # Projekt c. 1 - HTTP resolver doménových jmen
 # Autor: Marek Ziska, xziska03@stud.fit.vutbr.cz
 # Skupina: 2BIB
 # Datum 08.03.2020
##################################################

import socket
import re
import sys

HOST = '127.0.0.1'
if 0 < int(sys.argv[1]) < 65535:
    PORT = int(sys.argv[1])
else:
    print("Unsupported port, please use int in range of uint16!", file=sys.stderr)
    sys.exit()
DONE = True

####
 # Sets up socket object for various socket system calls, listens to any connections
 # incoming to {PORT}, receives data from this connections and sends them further for
 # parsing.
####
def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1025)
                        if not data or parse_done(data, conn):
                            break
    except KeyboardInterrupt:
        print("\nQuitting...")
    finally:
        exit()

####
 # Checks correctness of an IP
####
def ip_format(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error:
        return False
    return True

####
 # Resolves host name to ip, constructs final form of server response
####
def resolve_host_name(host):
    if ip_format(host):
        print("Wrong combination of operands!")
        return "400"
    try:
        host_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("There was an error resolving the host url", file=sys.stderr)
        return "404"
    return host + ':A=' + host_ip

####
 # Resolves ip to host name, constructs final form of server response
####
def resolve_host_ip(ip):
    if not ip_format(ip):
        print("Wrong combination of operands!")
        return "400"
    try:
        host_name = socket.gethostbyaddr(ip)
    except socket.gaierror:
        print("There was an error resolving the host ip", file=sys.stderr)
        return "404"
    return ip + ':PTR=' + host_name[0]

####
 # Sends response to client according to correctness of a request and used method
####
def send_response(response, conn, response_cat, http_type):
    if response == "400":
        conn.sendall(bytes("\r" + http_type + " 400 Bad Request\r\n\r\n", "UTF-8"))
    elif response == "404":
        conn.sendall(bytes("\r" + http_type + " 404 Not Found\r\n\r\n", "UTF-8"))
    elif response == "200post":
        conn.sendall(bytes("\r" + http_type + " 200 OK \r\n\r\n", "UTF-8"))
        for line in response_cat:
            conn.sendall(bytes(line + "\r\n", "UTF-8"))
    else:
        conn.sendall(bytes("\r" + http_type + " 200 OK\r\n\r\n" + response + "\r\n", "UTF-8"))

####
 # Processing GET request, parsing host/ip and contemplating final response
####
def response_get(fields, conn, http_type):
    byte_string = fields[1].decode('utf-8')
    match = re.search("^/resolve\?name=.*&type=.*$", byte_string)
    if not match:
        conn.sendall(bytes("\rHTTP/1.1 400 Bad Request \r\n", "UTF-8"))
        return

    host_string = re.sub('^/resolve\?name=', '', byte_string)
    line_parts = host_string.split('&type=')

    host = line_parts[0]
    req_type = line_parts[1]
    if req_type == "A":
        response = resolve_host_name(host)
    elif req_type == "PTR":
        response = resolve_host_ip(host)
    else:
        response = "400"
        print('Unknown request type', file=sys.stderr)

    send_response(response, conn, None, http_type)

####
 # Processing POST request, parsing host/ip and contemplating final response
####
def response_post(conn, data, http_type):
    fields = data.decode('utf-8').split("\r\n\r\n")
    hosts = fields[-1].split("\n")
    count = 0
    response = None
    response_cat = []
    for i in hosts:
        if i == "":
            count += 1
    if count > 1:
        print("There were empty rows in query list!", file=sys.stderr)
        response = "400"
    elif hosts[-1] == "":
        hosts.pop()
    elif count == 1:
        print("There was an empty row in query list!", file=sys.stderr)
        response = "400"

    if response is None:
        for line in hosts:
            line_parts = line.split(":")
            host = line_parts[0].strip()
            type = line_parts[1].strip()
            if type == "A":
                response_string = resolve_host_name(host)
                if response_string != "400" and response_string != "404":
                    response_cat.append(response_string)
                    response = "200post"
                elif response is None:
                    response = response_string
            elif type == "PTR":
                response_string = resolve_host_ip(host)
                if response_string != "400" and response_string != "404":
                    response_cat.append(response_string)
                    response = "200post"
                elif response is None:
                    response = response_string
            else:
                print('Unknown request type!', file=sys.stderr)
                response = "400"

    send_response(response, conn, response_cat, http_type)

####
 # Parsing request according to used method(either GET or POST)
 # and checks if incoming request isn't empty.
####
def parse_done(data, conn):
    fields = data.split()
    http_type = fields[2].decode('utf-8')
    if fields[0].decode('utf-8') == 'GET':
        response_get(fields, conn, http_type)
    elif fields[0].decode('utf-8') == 'POST':
        response_post(conn, data, http_type)
    elif int((fields[-3].decode('utf-8'))) == 0:
        conn.sendall(bytes("\r" + http_type + " 400 Bad Request\r\n", "UTF-8"))
    else:
        conn.sendall(bytes("\r" + http_type + " 405 Method Not Allowed\r\n", "UTF-8"))
    conn.close()
    return DONE

main()
