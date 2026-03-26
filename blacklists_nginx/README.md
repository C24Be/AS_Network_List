# nginx blacklists

Short: ready-to-use deny lists for nginx (mixed, IPv4-only, and IPv6-only).

## Download links

- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nginx/blacklist.conf
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nginx/blacklist-v4.conf
- https://raw.githubusercontent.com/C24Be/AS_Network_List/refs/heads/main/blacklists_nginx/blacklist-v6.conf

## How to use

1. Download one file (`blacklist.conf`, `blacklist-v4.conf`, or `blacklist-v6.conf`).
2. Include it in your `server` or `location` block:

```nginx
include /etc/nginx/blacklist.conf;
```

3. Test and reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```
