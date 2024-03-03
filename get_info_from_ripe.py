#!/usr/bin/env python3

import requests
from pylib.whois import whois_query

url          = "https://stat.ripe.net/data/country-resource-list/data.json?resource=RU&v4_format=prefix"

def get_data(json, file, attr, field, prefix=""):
    with open(file, 'w') as f:
        for x in json['data']['resources'][attr]:
            x = prefix+x.strip()
            name = "-no-description-"
            print(f"{x} {name}")
            f.write(str(x+" "+name) + '\n')

response = requests.get(url)
response.raise_for_status()

data = response.json()

get_data(data, 'auto/all-ru-asn.txt',  'asn',  'as-name', "AS")
get_data(data, 'auto/all-ru-ipv4.txt', 'ipv4', 'netname')
get_data(data, 'auto/all-ru-ipv6.txt', 'ipv6', 'netname')
