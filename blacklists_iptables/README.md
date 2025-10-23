# IPTables/IPSet Blacklist Configurations

Auto-generated ipset configuration files for blocking networks and IP addresses with iptables/ip6tables.

## Available Files

### IPv4 Only

- **`blacklist-v4.ipset`** - Contains only IPv4 networks (806 entries)

### IPv6 Only

- **`blacklist-v6.ipset`** - Contains only IPv6 networks (3 entries)

### Mixed IPv4/IPv6

- **`blacklist.ipset`** - Contains both IPv4 and IPv6 sets (809 total entries)

## Usage

### 1. Load the IPSet

```bash
# For IPv4 only
ipset restore < blacklist-v4.ipset

# For IPv6 only
ipset restore < blacklist-v6.ipset

# For both IPv4 and IPv6 (loads both sets)
ipset restore < blacklist.ipset
```

### 2. Apply IPTables Rules

```bash
# For IPv4
iptables -I INPUT -m set --match-set blacklist-v4 src -j DROP
iptables -I FORWARD -m set --match-set blacklist-v4 src -j DROP

# For IPv6
ip6tables -I INPUT -m set --match-set blacklist-v6 src -j DROP
ip6tables -I FORWARD -m set --match-set blacklist-v6 src -j DROP
```

### 3. Persist Rules (Optional)

To make the rules persistent across reboots:

**On Debian/Ubuntu:**

```bash
# Save iptables rules
iptables-save > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6

# Save ipset
ipset save > /etc/ipset.conf
```

**On RHEL/CentOS:**

```bash
# Save iptables rules
service iptables save
service ip6tables save

# Save ipset
ipset save > /etc/sysconfig/ipset
```

### 4. Update Existing Sets

To update the blacklist without restarting iptables:

```bash
# Flush and reload
ipset flush blacklist-v4
ipset restore < blacklist-v4.ipset
```

### 5. Remove Sets

```bash
# Remove IPv4 set
ipset flush blacklist-v4
ipset destroy blacklist-v4

# Remove IPv6 set
ipset flush blacklist-v6
ipset destroy blacklist-v6
```

## Performance Benefits

IPSet uses hash tables for O(1) lookup performance, making it ideal for large blacklists:

- Much faster than individual iptables rules
- Minimal CPU overhead
- Supports up to 65536 entries per set (configurable)
- Kernel-level implementation for maximum efficiency

## Automatic Updates

These files are automatically regenerated when the blacklists are updated via the GitHub Actions workflow.

## Source

Generated from the blacklist files in the `blacklists/` directory.
