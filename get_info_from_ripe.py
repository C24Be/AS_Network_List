#!/usr/bin/env python3

import requests
import socket

url          = "https://stat.ripe.net/data/country-resource-list/data.json?resource=RU&v4_format=prefix"
whois_server = "whois.ripe.net"

def whois_query(whois_server, query, get_field="netname"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((whois_server, 43))

    query = f"{query}\r\n"
    s.send(query.encode())

    response = ''
    while True:
        data = s.recv(4096)
        try:
            response += data.decode('utf-8')
        except:
            response += data.decode('latin-1')
        if not data:
            break
    s.close()

    for line in response.split('\n'):
        if line.startswith(get_field + ':'):
            return line.strip()

    return None

def get_data(json, file, attr, field, prefix=""):
    with open(file, 'w') as f:
        for x in json['data']['resources'][attr]:
            x = prefix+x.strip()
            response = whois_query(whois_server, x, field)
            name = response.split(':')[1].strip()
            print(f"{x} {name}")
            f.write(str(x+" "+name) + '\n')

response = requests.get(url)
response.raise_for_status()

data = response.json()

get_data(data, 'auto/all-ru-asn.txt',  'asn',  'as-name', "AS")
get_data(data, 'auto/all-ru-ipv4.txt', 'ipv4', 'netname')
get_data(data, 'auto/all-ru-ipv6.txt', 'ipv6', 'netname')
