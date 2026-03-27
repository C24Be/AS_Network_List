#!/usr/bin/env python3

import argparse
import re
import sys

import requests

from pylib.ip import convert_to_cidr
from pylib.whois import whois_query

def convert_to_raw_github_url(url):
    return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")


def iter_netnames(lines):
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^netname:", stripped, re.IGNORECASE):
            yield stripped.split(":", 1)[1].strip()
        else:
            yield stripped


def extract_netname(filename_or_url, quiet=False):
    if filename_or_url.startswith("http://") or filename_or_url.startswith("https://"):
        if "github.com" in filename_or_url:
            filename_or_url = convert_to_raw_github_url(filename_or_url)
        response = requests.get(filename_or_url, timeout=30)
        response.raise_for_status()
        lines = response.text.splitlines()
    else:
        with open(filename_or_url, "r", encoding="utf-8") as file:
            lines = file.readlines()

    for netname in iter_netnames(lines):
        response = whois_query(netname, "inetnum")
        if response is not None and len(response) > 0:
            if not quiet:
                print(f"# Network name: {netname}")
            for cidr in response:
                for network in convert_to_cidr(cidr):
                    print(network)

    return None


def build_parser():
    parser = argparse.ArgumentParser(description="Extract netname from file.")
    parser.add_argument("filename_or_url", help="The file or URL to extract netnames from.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Disable all output except prefixes.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        extract_netname(args.filename_or_url, quiet=args.quiet)
    except requests.RequestException as exc:
        print(f"ERROR: failed to fetch netname data: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: failed to read input: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
