#!/usr/bin/env python3

import requests
import argparse
from cymruwhois import Client

def get_as_prefixes(asn):
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prefixes = data['data']['prefixes']
        return [prefix['prefix'] for prefix in prefixes]
    else:
        return []

def get_as_whois(asn):
    c = Client()
    r = c.lookup(asn)
    return r.owner

def main():
    parser = argparse.ArgumentParser(description='./as_network_list.py -q AS61280')
    parser.add_argument('asn', help='The AS number to get prefixes for.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable all output except prefixes.')
    args = parser.parse_args()

    asn = args.asn
    prefixes = get_as_prefixes(asn)
    whois_info = get_as_whois(asn)

    if not args.quiet:
        print(f"Prefixes announced by {asn}:")
        print(f"Whois info for {asn}: {whois_info}")

    for prefix in prefixes:
        print(prefix)

if __name__ == "__main__":
    main()
