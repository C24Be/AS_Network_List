# nftables blacklists

Short: ready-to-use nftables set files (general and VK-only, separated by IPv4/IPv6).

## Download links

- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist.nft
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist-v4.nft
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist-v6.nft
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist-vk.nft
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist-vk-v4.nft
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nftables/blacklist-vk-v6.nft

## How to use

### 1) Protect VM from incoming connections (general blacklists)

Load either mixed or split general set files:

```bash
sudo nft -f blacklist.nft
# or:
sudo nft -f blacklist-v4.nft
sudo nft -f blacklist-v6.nft
```

Apply rules for inbound traffic to the VM:

```bash
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'
sudo nft add rule inet filter input ip saddr @blacklist_v4 counter reject
sudo nft add rule inet filter input ip6 saddr @blacklist_v6 counter reject
```

### 2) Block VK outbound traffic for VPN clients via NAT/FORWARD

Load either mixed or split VK set files:

```bash
sudo nft -f blacklist-vk.nft
# or:
sudo nft -f blacklist-vk-v4.nft
sudo nft -f blacklist-vk-v6.nft
```

Apply rules for forwarded client traffic (replace `<VPN_IFACE>`):

```bash
sudo nft add chain inet filter forward '{ type filter hook forward priority 0; policy accept; }'
sudo nft add rule inet filter forward iifname "<VPN_IFACE>" ip daddr @blacklist_vk_v4 counter reject
sudo nft add rule inet filter forward iifname "<VPN_IFACE>" ip6 daddr @blacklist_vk_v6 counter reject
```
