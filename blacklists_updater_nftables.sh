#!/bin/bash
# Generates nftables blacklist configurations from the main blacklist

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/blacklists_updater_common.subr"
INPUT_FILE="${BLACKLIST_FILE}"
OUTPUT_DIR="$SCRIPT_DIR/blacklists_nftables"

# Create required directories if they don't exist
mkdir -p "$OUTPUT_DIR" "${BLACKLISTS_DIR}"

echo "Generating nftables blacklists..."

build_vk_name_blacklists

# Generate mixed IPv4/IPv6 blacklist (recommended single-file load)
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

# Generate VK-only blacklists from the narrowed MAX/VK service name filter
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "${BLACKLIST_VK_FILE}" \
    "$OUTPUT_DIR/blacklist-vk.nft"
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "${BLACKLIST_VK_V4_FILE}" \
    "$OUTPUT_DIR/blacklist-vk-v4.nft"
python3 "$SCRIPT_DIR/generate_nft_blacklist.py" \
    "${BLACKLIST_VK_V6_FILE}" \
    "$OUTPUT_DIR/blacklist-vk-v6.nft"

# Clean up temp files
rm -f "$TMP_V4_FILE" "$TMP_V6_FILE"

echo "nftables blacklists generated successfully!"
echo ""
echo "VM incoming block examples (all lists, nftables):"
echo "  sudo nft -f $OUTPUT_DIR/blacklist.nft"
echo "  sudo nft -f $OUTPUT_DIR/blacklist-v4.nft"
echo "  sudo nft -f $OUTPUT_DIR/blacklist-v6.nft"
echo "  sudo nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'"
echo "  sudo nft add rule inet filter input ip saddr @blacklist_v4 counter reject"
echo "  sudo nft add rule inet filter input ip6 saddr @blacklist_v6 counter reject"
echo ""
echo "VK outbound block examples for VPN clients via NAT (nftables):"
echo "  sudo nft -f $OUTPUT_DIR/blacklist-vk.nft"
echo "  sudo nft -f $OUTPUT_DIR/blacklist-vk-v4.nft"
echo "  sudo nft -f $OUTPUT_DIR/blacklist-vk-v6.nft"
echo "  sudo nft add chain inet filter forward '{ type filter hook forward priority 0; policy accept; }'"
echo "  sudo nft add rule inet filter forward iifname \"<VPN_IFACE>\" ip daddr @blacklist_vk_v4 counter reject"
echo "  sudo nft add rule inet filter forward iifname \"<VPN_IFACE>\" ip6 daddr @blacklist_vk_v6 counter reject"
echo ""
echo "Tip: Do not install Messenger MAX on the same phone/device that has VPN access configured."
