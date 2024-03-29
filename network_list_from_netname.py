#!/usr/bin/env python3

import argparse
import requests
import re
from   pylib.whois import whois_query
from   pylib.ip    import convert_to_cidr

def convert_to_raw_github_url(url):
    return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")

def extract_netname(filename_or_url):
    if filename_or_url.startswith('http://') or filename_or_url.startswith('https://'):
        if 'github.com' in filename_or_url:
            filename_or_url = convert_to_raw_github_url(filename_or_url)
        response = requests.get(filename_or_url)
        lines = response.text.split('\n')
    else:
        with open(filename_or_url, 'r') as file:
            lines = file.readlines()

    for line in lines:
        if re.match(r'^netname:', line):
            netname = line.split(':')[1].strip()
            response = whois_query(netname, "inetnum")
            if response is not None and len(response) > 0:
                if not args.quiet:
                    print(f"# Network name: {netname}")
                for cidr in response:
                    net = convert_to_cidr(cidr)
                    net = net[0]
                    print(net)

    return None

parser = argparse.ArgumentParser(description='Extract netname from file.')
parser.add_argument('filename_or_url', help='The file or URL to extract netnames from.')
parser.add_argument('-q', '--quiet', action='store_true', help='Disable all output except prefixes.')
args = parser.parse_args()

extract_netname(args.filename_or_url)
