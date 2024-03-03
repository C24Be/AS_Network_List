#!/usr/bin/env python3

import argparse
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
    limit = args.limit
    count = 0
    with open(file, 'w') as f:
        for x in json['data']['resources'][attr]:
            count += 1
            x = prefix+x.strip()
            if count > limit:
                response = None
            else:
                response = whois_query(whois_server, x, field)
            if response is None:
                name = "-no-description-"
            else:
                name = response.split(':')[1].strip()
            print(f"{x} {name}")
            f.write(str(x+" "+name) + '\n')

parser = argparse.ArgumentParser()
parser.add_argument('--asn', action='store_true', help='Run the ASN query')
parser.add_argument('--ipv4', action='store_true', help='Run the IPv4 query')
parser.add_argument('--ipv6', action='store_true', help='Run the IPv6 query')
parser.add_argument('--all', action='store_true', help='Run all queries')
parser.add_argument('--limit', type=int, help='Limit the number of whois queries to prevent blacklisting from whois servers', default=2500)
args = parser.parse_args()

if not (args.asn or args.ipv4 or args.ipv6 or args.all):
    parser.print_help()
    exit()

response = requests.get(url)
response.raise_for_status()

data = response.json()

if args.asn or args.all:
    get_data(data, 'auto/all-ru-asn.txt',  'asn',  'as-name', "AS")

if args.ipv4 or args.all:
    get_data(data, 'auto/all-ru-ipv4.txt', 'ipv4', 'netname')

if args.ipv6 or args.all:
    get_data(data, 'auto/all-ru-ipv6.txt', 'ipv6', 'netname')
