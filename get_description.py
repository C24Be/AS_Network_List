#!/usr/bin/env python3

import argparse
import re
from pylib.whois import whois_query

def resolve(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        f.close()
    limit = args.limit
    count = 0
    for i in range(len(lines)):
        if re.match(r'.*-no-description-.*', lines[i]):
            count += 1
            line = lines[i].split()
            if count > limit:
                break
            else:
                if re.match(r'^AS.*', line[0]):
                    response = whois_query(line[0], "as-name")
                else:
                    response = whois_query(line[0], "netname")
                if response is None:
                    name = "-not-found-"
                else:
                    name = response.split(':')[1].strip()
                print(line[0] + " " + name)
                lines[i]=str(line[0] + " " + name + "\n")
    with open(filename, 'w') as f:
        f.writelines(lines)
        f.close()

parser = argparse.ArgumentParser(description='Resolve names for ASNs and Networks.')
parser.add_argument('filename', help='The file with list of the ASNs or Networks.')
parser.add_argument('--limit', type=int, help='Limit the number of whois queries to prevent blacklisting from whois servers', default=2500)
args = parser.parse_args()

if not (args.filename):
    parser.print_help()
    exit()

resolve(args.filename)
