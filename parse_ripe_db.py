#!/usr/bin/env python3

import argparse
import json
import sys

from pylib.ip import convert_to_cidr

country = "RU"


def normalize_record(record):
    if not record:
        return None
    if record.get("country") != country:
        return None

    normalized = dict(record)
    normalized["inetnum"] = convert_to_cidr(record["inetnum"])
    return normalized


def parse(filename, output_text, output_json):
    c_list = []
    record = {}
    with open(filename, "r", encoding="latin-1") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("inetnum:"):
            normalized = normalize_record(record)
            if normalized is not None:
                c_list.append(normalized)
            record = {}
            record["inetnum"] = line.split("inetnum:", 1)[1].strip()
            record["descr"] = ""
            record["netname"] = ""
            record["country"] = ""
            record["org"] = ""
        if line.startswith("netname:"):
            record["netname"] = line.split("netname:", 1)[1].strip()
        if line.startswith("descr:"):
            record["descr"] = str(record["descr"].strip() + " " + line.split("descr:", 1)[1].strip()).strip()
        if line.startswith("mnt-by:"):
            record["netname"] = str(record["netname"].strip() + " " + line.split("mnt-by:", 1)[1].strip()).strip()
        if line.startswith("country:"):
            record["country"] = line.split("country:", 1)[1].strip()
        if line.startswith("org:"):
            record["org"] = line.split("org:", 1)[1].strip()

    normalized = normalize_record(record)
    if normalized is not None:
        c_list.append(normalized)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(c_list, f, indent=4)

    with open(output_text, "w", encoding="utf-8") as f:
        for item in c_list:
            for net in item["inetnum"]:
                f.write(net + " " + item["netname"] + " (" + item["org"] + ") [" + item["descr"] + "]\n")


def build_parser():
    parser = argparse.ArgumentParser(description="Parse RIPE DB for getting a list of RU networks.")
    parser.add_argument("filename", help="ripe.db.inetnum file to parse.")
    parser.add_argument("output_text", help="write text db to...")
    parser.add_argument("output_json", help="write json db to...")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        parse(args.filename, args.output_text, args.output_json)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
