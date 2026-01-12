#!/bin/bash
# Generates nftables blacklist configurations from the main blacklist

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="$SCRIPT_DIR/blacklists/blacklist.txt"
OUTPUT_DIR="$SCRIPT_DIR/blacklists_nftables"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Generating nftables blacklists..."

# Generate mixed IPv4/IPv6 blacklist
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$INPUT_FILE" \
    "$OUTPUT_DIR/blacklist.nft"

# Generate IPv4-only blacklist
grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$INPUT_FILE" > /tmp/blacklist-v4.txt || true
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    /tmp/blacklist-v4.txt \
    "$OUTPUT_DIR/blacklist-v4.nft"

# Generate IPv6-only blacklist
grep -E '^[0-9a-fA-F:]+:' "$INPUT_FILE" > /tmp/blacklist-v6.txt || true
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    /tmp/blacklist-v6.txt \
    "$OUTPUT_DIR/blacklist-v6.nft"

# Clean up temp files
rm -f /tmp/blacklist-v4.txt /tmp/blacklist-v6.txt

echo "nftables blacklists generated successfully!"
