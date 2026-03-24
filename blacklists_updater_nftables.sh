#!/bin/bash
# Generates nftables blacklist configurations from the main blacklist

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="$SCRIPT_DIR/blacklists/blacklist.txt"
OUTPUT_DIR="$SCRIPT_DIR/blacklists_nftables"

# Source files for name-based VK filtering
AUTO_ALL_V4_FILE="$SCRIPT_DIR/auto/all-ru-ipv4.txt"
AUTO_ALL_V6_FILE="$SCRIPT_DIR/auto/all-ru-ipv6.txt"
AUTO_RIPE_V4_FILE="$SCRIPT_DIR/auto/ripe-ru-ipv4.txt"
VK_NAME_PATTERN='VK[[:space:]-]*CLOUD|VKCOMPANY|VKONTAKTE'

# Additional VK-only text blacklists
VK_INPUT_FILE="$SCRIPT_DIR/blacklists/blacklist-vk.txt"
VK_INPUT_V4_FILE="$SCRIPT_DIR/blacklists/blacklist-vk-v4.txt"
VK_INPUT_V6_FILE="$SCRIPT_DIR/blacklists/blacklist-vk-v6.txt"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Generating nftables blacklists..."

# Build additional VK-only blacklist from network names in auto/*.txt files
TMP_VK_FILE="$(mktemp "$SCRIPT_DIR/blacklists/.blacklist-vk.XXXXXX")"
for source_file in "$AUTO_ALL_V4_FILE" "$AUTO_ALL_V6_FILE" "$AUTO_RIPE_V4_FILE"; do
    [[ -f "$source_file" ]] || continue
    awk -v pattern="$VK_NAME_PATTERN" 'BEGIN { IGNORECASE = 1 } $0 ~ pattern { print $1 }' "$source_file" >> "$TMP_VK_FILE"
done
sort -u "$TMP_VK_FILE" > "$VK_INPUT_FILE"
grep ':' "$VK_INPUT_FILE" | sort -u > "$VK_INPUT_V6_FILE" || true
grep -v ':' "$VK_INPUT_FILE" | sort -u > "$VK_INPUT_V4_FILE" || true
rm -f "$TMP_VK_FILE"

# Generate mixed IPv4/IPv6 blacklist
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$INPUT_FILE" \
    "$OUTPUT_DIR/blacklist.nft"

# Generate IPv4-only blacklist
TMP_V4_FILE="/tmp/blacklist-v4.txt"
TMP_V6_FILE="/tmp/blacklist-v6.txt"
grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$INPUT_FILE" > "$TMP_V4_FILE" || true
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$TMP_V4_FILE" \
    "$OUTPUT_DIR/blacklist-v4.nft"

# Generate IPv6-only blacklist
grep -E '^[0-9a-fA-F:]+:' "$INPUT_FILE" > "$TMP_V6_FILE" || true
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$TMP_V6_FILE" \
    "$OUTPUT_DIR/blacklist-v6.nft"

# Generate VK-only blacklists (network names: VK Cloud / VKCOMPANY / VKONTAKTE)
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$VK_INPUT_FILE" \
    "$OUTPUT_DIR/blacklist-vk.nft"
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$VK_INPUT_V4_FILE" \
    "$OUTPUT_DIR/blacklist-vk-v4.nft"
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "$VK_INPUT_V6_FILE" \
    "$OUTPUT_DIR/blacklist-vk-v6.nft"

# Clean up temp files
rm -f "$TMP_V4_FILE" "$TMP_V6_FILE"

echo "nftables blacklists generated successfully!"
