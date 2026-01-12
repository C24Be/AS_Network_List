# nftables Blacklist Configuration

This folder contains nftables blacklist configurations generated from Russian government agency network lists.

## Available Files

- `blacklist.nft` - Mixed IPv4/IPv6 blacklist (**daily generated**)
- `blacklist-v4.nft` - IPv4-only blacklist (**daily generated**)
- `blacklist-v6.nft` - IPv6-only blacklist (**daily generated**)

## Quick Start

### Download and Load
````bash
# Download the blacklist
wget https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_nftables/blacklist.nft

# Load the configuration
sudo nft -f blacklist.nft

# Verify it's loaded
sudo nft list ruleset
````

### Automatic Updates

Add to crontab for daily updates:
````bash
0 2 * * * wget -O /etc/nftables.d/blacklist.nft https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_nftables/blacklist.nft && nft -f /etc/nftables.d/blacklist.nft
````

## Configuration Details

The generated nftables configuration uses:
- **Sets with interval flag** for efficient CIDR matching
- **Named sets** (`blacklist_v4` and `blacklist_v6`) for easy management
- **Counter** directive to track dropped packets
- **Stateful filtering** to allow established connections

### Configuration Structure
table inet filter {
set blacklist_v4 {
type ipv4_addr
flags interval
elements = { 1.2.3.0/24, 5.6.7.0/24, ... }
}
set blacklist_v6 {
    type ipv6_addr
    flags interval
    elements = { 2001:db8::/32, ... }
}

chain input {
    type filter hook input priority 0;
    policy accept;
    
    ct state { established, related } accept
    
    ip saddr @blacklist_v4 counter drop
    ip6 saddr @blacklist_v6 counter drop
}
}

## Integration Options

### Option 1: Standalone Configuration

Load the blacklist as a complete ruleset:
````bash
sudo nft -f blacklist.nft
````

### Option 2: Include in Existing Configuration

If you have an existing nftables configuration:

1. Copy only the set definitions from the generated file
2. Add set lookups to your existing input chain:
````bash
ip saddr @blacklist_v4 counter drop
ip6 saddr @blacklist_v6 counter drop
````

### Option 3: Persistent Configuration

For systemd-based systems:
````bash
# Copy to nftables config directory
sudo cp blacklist.nft /etc/nftables.d/

# Edit /etc/nftables.conf to include:
# include "/etc/nftables.d/blacklist.nft"

# Enable and restart
sudo systemctl enable nftables
sudo systemctl restart nftables
````

## Checking IPs Against the Blacklist

Use the `check_nft_blacklist.py` script to verify if an IP is blocked:
````bash
# Check an IPv4 address
python3 check_nft_blacklist.py blacklist.nft 192.168.1.1

# Check an IPv6 address
python3 check_nft_blacklist.py blacklist.nft 2001:db8::1
````

## Monitoring

### View Dropped Packets
````bash
# View all rules with counters
sudo nft list chain inet filter input -a

# Monitor in real-time
sudo nft monitor
````

### Check Set Contents
````bash
# View IPv4 blacklist
sudo nft list set inet filter blacklist_v4

# View IPv6 blacklist
sudo nft list set inet filter blacklist_v6
````

## Advantages of nftables

- **Better Performance**: O(1) lookup time with sets vs O(n) for sequential rules
- **Lower Memory Usage**: More efficient than iptables for large rulesets
- **Atomic Updates**: All rules updated in a single transaction
- **Modern Syntax**: Cleaner, more readable configuration
- **Unified Tool**: Single tool for IPv4, IPv6, and ARP filtering

## File Format Comparison

| Format | Use Case | Performance | Memory |
|--------|----------|-------------|--------|
| **nftables** | Modern firewalls | Excellent | Low |
| **iptables** | Legacy systems | Good | Medium |
| **nginx** | Web layer | Good | Low |

## Troubleshooting

### Configuration Won't Load
````bash
# Check syntax
sudo nft -c -f blacklist.nft

# View detailed errors
sudo nft -f blacklist.nft 2>&1 | less
````

### Rules Not Blocking Traffic
````bash
# Verify sets are populated
sudo nft list set inet filter blacklist_v4 | wc -l

# Check rule priority
sudo nft list chain inet filter input

# Test with logging temporarily
sudo nft add rule inet filter input ip saddr @blacklist_v4 log prefix "BLOCKED: "
````

### Performance Issues

If experiencing performance problems with very large sets:

1. Consider splitting into multiple smaller sets
2. Use `blacklist-v4.nft` or `blacklist-v6.nft` if only one protocol is needed
3. Ensure kernel supports nftables fully (Linux 4.0+)

## Additional Resources

- [nftables Wiki](https://wiki.nftables.org/)
- [nftables Quick Reference](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes)
- [Netfilter Documentation](https://www.netfilter.org/documentation/)

## Contributing

Found an issue or have suggestions? Please open an issue or submit a pull request!
