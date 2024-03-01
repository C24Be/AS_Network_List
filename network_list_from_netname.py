#!/usr/bin/env python3

import socket
import argparse
import requests
import ipaddress
import re

whois_server = "whois.ripe.net"

def whois_query(whois_server, query):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((whois_server, 43))

    # Prepare the query
    query = f"{query}\r\n"
    s.send(query.encode())

    # Collect the response
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

    # Extract the inetnum line
    for line in response.split('\n'):
        if line.startswith('inetnum'):
            return line.strip()

    return None

def convert_to_raw_github_url(url):
    return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")

def convert_to_cidr(ip_range):
    start_ip, end_ip = ip_range.split(' - ')
    start_ip = ipaddress.IPv4Address(start_ip)
    end_ip = ipaddress.IPv4Address(end_ip)
    cidrs = ipaddress.summarize_address_range(start_ip, end_ip)
    return [str(cidr) for cidr in cidrs]

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
        if re.match(r'.*netname:', line):
            response = whois_query(whois_server, line.split(':')[1].strip())
            if response is not None:
                ip_range = response.split(':')[1].strip()
                cidrs = convert_to_cidr(ip_range)
                for cidr in cidrs:
                    print(cidr)

    return None

def main():
    parser = argparse.ArgumentParser(description='Extract netname from file.')
    parser.add_argument('filename_or_url', help='The file to extract netname from.')
    args = parser.parse_args()

    extract_netname(args.filename_or_url)

if __name__ == "__main__":
    main()
