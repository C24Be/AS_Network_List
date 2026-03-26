# linux route blacklists

Short: ready-to-use route files for VK networks with loopback routing (IPv4/IPv6).

## Download links

- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_route/blacklist-vk-v4.routes
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_route/blacklist-vk-v6.routes

## How to use

1. Download both route files.
2. Apply routes as root:

```bash
sudo sh blacklist-vk-v4.routes
sudo sh blacklist-vk-v6.routes
```

3. Verify routes are present:

```bash
ip route | grep -E '127\.0\.0\.1.*lo'
ip -6 route | grep -E '::1'
```
