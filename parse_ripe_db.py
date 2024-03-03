#!/usr/bin/env python3

import argparse
import re
import json
from   pylib.ip import convert_to_cidr

country = "RU"

def parse(filename, output_text, output_json):
    cList = []
    record = {}
    with open(filename, 'r', encoding='latin-1') as f:
        lines = f.readlines()
        f.close()
    for line in lines:
        if re.match(r'^inetnum:', line):
            if record:
                record['inetnum'] = convert_to_cidr(record['inetnum'])
                if record['country'] == country:
#                    print(record)
                    cList.append(record)
            record = {}
            record['inetnum'] = line.split('inetnum:', 1)[1].strip()
            record['descr'] = ''
            record['netname'] = ''
            record['country'] = ''
            record['org'] = ''
        if re.match(r'^netname:', line):
            record['netname'] = line.split('netname:', 1)[1].strip()
        if re.match(r'^descr:', line):
            record['descr'] = str(record['descr'].strip() + ' ' + line.split('descr:', 1)[1].strip()).strip()
        if re.match(r'^mnt-by:', line):
            record['netname'] = str(record['netname'].strip() + ' ' + line.split('mnt-by:', 1)[1].strip()).strip()
        if re.match(r'^country:', line):
            record['country'] = line.split('country:', 1)[1].strip()
        if re.match(r'^org:', line):
            record['org'] = line.split('org:', 1)[1].strip()
    if record:
        cList.append(record)

    with open(output_json, 'w') as f:
        json.dump(cList, f, indent=4)
        f.close()

    with open(output_text, 'w') as f:
        for record in cList:
            for net in record['inetnum']:
                f.write(net + ' ' + record['netname'] + ' (' + record['org'] + ') [' + record['descr'] + ']\n')
        f.close()

parser = argparse.ArgumentParser(description='Parse RIPE DB for getting a list of RU networks.')
parser.add_argument('filename', help='ripe.db.inetnum file to parse.')
parser.add_argument('output_text', help='write text db to...')
parser.add_argument('output_json', help='write json do to...')
args = parser.parse_args()

if not (args.filename):
    parser.print_help()
    exit()

parse(args.filename, args.output_text, args.output_json)
