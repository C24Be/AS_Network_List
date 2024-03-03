#!/usr/bin/env python3

import argparse
import requests
from pylib.whois import whois_query

url          = "https://stat.ripe.net/data/country-resource-list/data.json?resource=RU&v4_format=prefix"

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
                response = whois_query(x, field)
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
