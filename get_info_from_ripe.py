#!/usr/bin/env python3

import requests

url           = "https://stat.ripe.net/data/country-resource-list/data.json?resource=RU&v4_format=prefix"

out_file_asn  = "auto/all-ru-asn.txt"
out_file_ipv4 = "auto/all-ru-ipv4.txt"
out_file_ipv6 = "auto/all-ru-ipv6.txt"

response = requests.get(url)
response.raise_for_status()

data = response.json()

with open(out_file_asn, 'w') as f:
    for asn in data['data']['resources']['asn']:
        f.write(str("AS"+asn) + '\n')

with open(out_file_ipv4, 'w') as f:
    for ipv4 in data['data']['resources']['ipv4']:
        f.write(str(ipv4) + '\n')

with open(out_file_ipv6, 'w') as f:
    for ipv6 in data['data']['resources']['ipv6']:
        f.write(str(ipv6) + '\n')
