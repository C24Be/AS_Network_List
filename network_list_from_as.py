#!/usr/bin/env python3

import argparse
import re
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pylib.whois import WhoisError, whois_query

ASN_RE = re.compile(r"\bAS\d+\b", re.IGNORECASE)
ANNOUNCED_PREFIXES_URL = "https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"


def build_session(backoff_factor=5):
    retry = Retry(
        total=5,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


SESSION = build_session()


def get_as_prefixes(asn):
    response = SESSION.get(ANNOUNCED_PREFIXES_URL.format(asn=asn), timeout=30)
    response.raise_for_status()
    data = response.json()
    prefixes = data["data"]["prefixes"]
    return [prefix["prefix"] for prefix in prefixes]

def convert_to_raw_github_url(url):
    return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")


def normalize_asn(value):
    match = ASN_RE.search(value)
    if match:
        return match.group(0).upper()
    return None


def print_prefixes(asn, quiet=False):
    normalized_asn = normalize_asn(asn)
    if normalized_asn is None:
        return

    if not quiet:
        print(f"# Networks announced by {normalized_asn}")
        response = whois_query(normalized_asn, "as-name", True)
        if response is not None:
            info = response.strip()
            print(f"# AS-Name (ORG): {info}")
    prefixes = get_as_prefixes(normalized_asn)
    for prefix in prefixes:
        print(prefix)


def extract_asses(asn_filename_or_url, quiet=False):
    if normalize_asn(asn_filename_or_url) and not asn_filename_or_url.startswith(("http://", "https://")):
        print_prefixes(asn_filename_or_url, quiet=quiet)

        return None

    if asn_filename_or_url.startswith("http://") or asn_filename_or_url.startswith("https://"):
        if "github.com" in asn_filename_or_url:
            asn_filename_or_url = convert_to_raw_github_url(asn_filename_or_url)
        response = requests.get(asn_filename_or_url, timeout=30)
        response.raise_for_status()
        lines = response.text.splitlines()
    else:
        with open(asn_filename_or_url, "r", encoding="utf-8") as file:
            lines = file.readlines()

    for line in lines:
        normalized_asn = normalize_asn(line)
        if normalized_asn:
            print_prefixes(normalized_asn, quiet=quiet)

    return None


def build_parser():
    parser = argparse.ArgumentParser(description="./network_list_from_as.py -q AS61280")
    parser.add_argument("asn_filename_or_url", help="The AS number to get networks / The file or URL to extract AS numbers from.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Disable all output except prefixes.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        extract_asses(args.asn_filename_or_url, quiet=args.quiet)
    except (requests.RequestException, WhoisError) as exc:
        print(f"ERROR: failed to fetch ASN data: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: failed to read input: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
