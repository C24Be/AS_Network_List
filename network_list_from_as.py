#!/usr/bin/env python3

import requests
import argparse
import re
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

def convert_to_raw_github_url(url):
    return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")

def print_prefixes(asn):
    line = re.sub(r'[^AS0-9]', '', asn)
    if not args.quiet:
        print(f"# Networks announced by {line}")
    prefixes = get_as_prefixes(line)
    for prefix in prefixes:
        print(prefix)

def extract_asses(asn_filename_or_url):
    if asn_filename_or_url.startswith('AS'):
        print_prefixes(asn_filename_or_url)

        return None

    if asn_filename_or_url.startswith('http://') or asn_filename_or_url.startswith('https://'):
        if 'github.com' in asn_filename_or_url:
            asn_filename_or_url = convert_to_raw_github_url(asn_filename_or_url)
        response = requests.get(asn_filename_or_url)
        lines = response.text.split('\n')
    else:
        with open(asn_filename_or_url, 'r') as file:
            lines = file.readlines()

    for line in lines:
        if re.match(r'^AS.*', line):
            print_prefixes(line)

    return None

parser = argparse.ArgumentParser(description='./as_network_list.py -q AS61280')
parser.add_argument('asn_filename_or_url', help='The AS number to get networks / The file or URL to extract AS numbers from.')
parser.add_argument('-q', '--quiet', action='store_true', help='Disable all output except prefixes.')
args = parser.parse_args()

extract_asses(args.asn_filename_or_url)
