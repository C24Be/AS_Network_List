#!/usr/bin/env python3
"""
check_nft_blacklist.py
Checks if an IP address is in the nftables blacklist configuration.
Usage:
  check_nft_blacklist.py nft_bl.conf 192.168.1.1
  check_nft_blacklist.py nft_bl.conf 2001:db8::1
"""

import sys
import re
from ipaddress import ip_address, ip_network, AddressValueError
from pathlib import Path

def parse_nft_config(config_path):
    """Extract IPv4 and IPv6 prefixes from nftables config."""
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    content = p.read_text(encoding="utf-8")
    v4_prefixes = []
    v6_prefixes = []
    
    # Parse IPv4 set (blacklist_v4)
    v4_match = re.search(
        r'set blacklist_v4\s*\{[^}]*elements\s*=\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    if v4_match:
        elements = v4_match.group(1)
        # Extract all CIDR notations
        for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', elements):
            try:
                v4_prefixes.append(ip_network(match.group(1), strict=False))
            except Exception as e:
                print(f"Warning: Could not parse IPv4 prefix '{match.group(1)}': {e}", file=sys.stderr)
    
    # Parse IPv6 set (blacklist_v6)
    v6_match = re.search(
        r'set blacklist_v6\s*\{[^}]*elements\s*=\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    if v6_match:
        elements = v6_match.group(1)
        # Extract all IPv6 CIDR notations
        for match in re.finditer(r'([0-9a-fA-F:]+(?:/\d+)?)', elements):
            try:
                v6_prefixes.append(ip_network(match.group(1), strict=False))
            except Exception as e:
                # Skip false matches from comments or other text
                pass
    
    return v4_prefixes, v6_prefixes

def check_ip_in_blacklist(ip_addr, v4_prefixes, v6_prefixes):
    """Check if IP address is in any of the blacklist prefixes."""
    try:
        addr = ip_address(ip_addr)
    except AddressValueError as e:
        raise ValueError(f"Invalid IP address: {ip_addr} ({e})")
    
    prefixes = v4_prefixes if addr.version == 4 else v6_prefixes
    
    for prefix in prefixes:
        if addr in prefix:
            return True, prefix
    
    return False, None

def main(argv):
    if len(argv) < 3:
        print("Usage: python3 check_nft_blacklist.py <nft_config.conf> <ip_address>")
        print("Examples:")
        print("  check_nft_blacklist.py nft_bl.conf 192.168.1.1")
        print("  check_nft_blacklist.py nft_bl.conf 2001:db8::1")
        return 2
    
    config_file = argv[1]
    ip_to_check = argv[2]
    
    # Parse the nftables config
    try:
        print(f"Loading blacklist from: {config_file}")
        v4_prefixes, v6_prefixes = parse_nft_config(config_file)
        print(f"Loaded {len(v4_prefixes)} IPv4 prefixes and {len(v6_prefixes)} IPv6 prefixes")
    except Exception as e:
        print(f"ERROR: Could not parse config file: {e}", file=sys.stderr)
        return 3
    
    # Check if IP is in blacklist
    try:
        is_blocked, matching_prefix = check_ip_in_blacklist(ip_to_check, v4_prefixes, v6_prefixes)
        
        print(f"\nChecking IP: {ip_to_check}")
        print("-" * 50)
        
        if is_blocked:
            print(f"✗ BLOCKED - IP is in blacklist")
            print(f"  Matching prefix: {matching_prefix}")
            return 1
        else:
            print(f"✓ OK - IP is NOT in blacklist")
            return 0
            
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 4

if __name__ == "__main__":
    sys.exit(main(sys.argv))
