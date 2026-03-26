# iptables/ipset blacklists

Short: ready-to-use ipset files for iptables/ip6tables (general and VK-only, separated by IPv4/IPv6).

## Download links

- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_iptables/blacklist-v4.ipset
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_iptables/blacklist-v6.ipset
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_iptables/blacklist-vk-v4.ipset
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_iptables/blacklist-vk-v6.ipset

## How to use

### 1) Protect VM from incoming connections (general blacklists)

Load IPv4 and IPv6 sets:

```bash
ipset restore < blacklist-v4.ipset
ipset restore < blacklist-v6.ipset
```

Apply inbound rules to traffic connecting to the VM and forwarded through the host:

```bash
iptables -I INPUT -m set --match-set blacklist-v4 src -m conntrack --ctstate NEW -j DROP
iptables -I FORWARD -m set --match-set blacklist-v4 src -m conntrack --ctstate NEW -j DROP
ip6tables -I INPUT -m set --match-set blacklist-v6 src -m conntrack --ctstate NEW -j DROP
ip6tables -I FORWARD -m set --match-set blacklist-v6 src -m conntrack --ctstate NEW -j DROP
```

### 2) Block VK outbound traffic

Load VK IPv4 and IPv6 sets:

```bash
ipset restore < blacklist-vk-v4.ipset
ipset restore < blacklist-vk-v6.ipset
```

Apply OUTPUT rules for traffic originated on this host:

```bash
iptables -I OUTPUT -m set --match-set blacklist-vk-v4 dst -j REJECT
ip6tables -I OUTPUT -m set --match-set blacklist-vk-v6 dst -j REJECT
```

If you also need to block forwarded VPN-client traffic via NAT, add FORWARD rules (replace `<VPN_IFACE>`):

```bash
iptables -I FORWARD -i <VPN_IFACE> -m set --match-set blacklist-vk-v4 dst -j REJECT
ip6tables -I FORWARD -i <VPN_IFACE> -m set --match-set blacklist-vk-v6 dst -j REJECT
```
