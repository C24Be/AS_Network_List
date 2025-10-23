# Nginx Blacklist Configurations

Auto-generated nginx configuration files for blocking networks and IP addresses.

## Available Files

### Mixed IPv4/IPv6

- **`blacklist.conf`** - Contains both IPv4 and IPv6 deny rules (809 entries)

### IPv4 Only

- **`blacklist-v4.conf`** - Contains only IPv4 deny rules (806 entries)

### IPv6 Only

- **`blacklist-v6.conf`** - Contains only IPv6 deny rules (3 entries)

## Usage

### Basic Usage

Include the desired configuration file in your nginx `server` or `location` block:

```nginx
server {
    listen 80;
    server_name example.com;

    # Include the blacklist
    include /path/to/blacklist.conf;

    location / {
        # your configuration
    }
}
```

### Separate IPv4/IPv6 Files

For more granular control, use separate files:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com;

    # Include both IPv4 and IPv6 blacklists
    include /path/to/blacklist-v4.conf;
    include /path/to/blacklist-v6.conf;

    location / {
        # your configuration
    }
}
```

### HTTP Block Level

Apply the blacklist globally to all virtual hosts:

```nginx
http {
    # Apply blacklist globally
    include /path/to/blacklist.conf;

    server {
        listen 80;
        server_name example.com;
        # ...
    }

    server {
        listen 80;
        server_name another.com;
        # ...
    }
}
```

### Location Block Level

For selective blocking within specific locations:

```nginx
server {
    listen 80;
    server_name example.com;

    location /admin {
        # Apply blacklist only to admin area
        include /path/to/blacklist.conf;
        # ...
    }

    location /public {
        # Public area without blacklist
        # ...
    }
}
```

## Testing Configuration

After adding the blacklist, always test your nginx configuration:

```bash
# Test configuration
nginx -t

# Reload nginx if test passes
nginx -s reload
# or
systemctl reload nginx
```

## Custom Response

By default, denied IPs receive a connection drop. To customize the response:

```nginx
server {
    listen 80;
    server_name example.com;

    # Return custom error page
    error_page 403 /403.html;

    include /path/to/blacklist.conf;

    location = /403.html {
        root /usr/share/nginx/html;
        internal;
    }
}
```

Note: For large blacklists, using `deny` directives (as in these files) is more efficient than `if` statements.

## Performance Considerations

- **Deny directives** are processed in order and stop at the first match
- For optimal performance, most frequently matched IPs should be at the top
- Current files are sorted for consistency
- Nginx handles hundreds of deny rules efficiently
- For very large blacklists (10,000+ entries), consider using:
  - Nginx GeoIP2 module for geographic blocking
  - nftables/iptables at the firewall level for better performance
  - Stream module for TCP/UDP level blocking

## Integration Examples

### Docker Deployment

```dockerfile
FROM nginx:alpine

# Copy blacklist
COPY blacklist.conf /etc/nginx/blacklist.conf

# Copy nginx config that includes the blacklist
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-blacklist
data:
  blacklist.conf: |
    # Include blacklist content here
    deny 109.124.119.88/29;
    deny 109.124.66.128/30;
    # ...
```

### Automated Updates

Set up a cron job to automatically fetch the latest blacklist:

```bash
#!/bin/bash
# /etc/cron.daily/update-nginx-blacklist

# Download latest blacklist
wget -q https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_nginx/blacklist.conf \
  -O /etc/nginx/blacklist.conf.new

# Test nginx configuration
nginx -t -c /etc/nginx/nginx.conf

# If test passes, reload nginx
if [ $? -eq 0 ]; then
    mv /etc/nginx/blacklist.conf.new /etc/nginx/blacklist.conf
    systemctl reload nginx
    echo "Blacklist updated successfully"
else
    rm /etc/nginx/blacklist.conf.new
    echo "Nginx config test failed, blacklist not updated"
fi
```

## Logging Blocked Requests

To log denied requests:

```nginx
server {
    listen 80;
    server_name example.com;

    # Custom log format for denied IPs
    log_format blocked '$remote_addr - $remote_user [$time_local] '
                      '"$request" 403 0 '
                      '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/blocked.log blocked;

    include /path/to/blacklist.conf;

    location / {
        # your configuration
    }
}
```

## Monitoring

Check how many IPs are being blocked:

```bash
# Count deny rules
grep -c "deny" /path/to/blacklist.conf

# Check blocked access logs
tail -f /var/log/nginx/blocked.log

# Count blocked requests today
grep "$(date +%d/%b/%Y)" /var/log/nginx/access.log | grep " 403 " | wc -l
```

## Troubleshooting

### Configuration Test Fails

```bash
# Check syntax
nginx -t

# Check for duplicate includes
grep -r "include.*blacklist" /etc/nginx/

# Verify file permissions
ls -l /path/to/blacklist.conf
```

### Legitimate Users Blocked

Check if their IP is in the blacklist:

```bash
grep "YOUR_IP" /path/to/blacklist.conf
```

Whitelist specific IPs before applying the blacklist:

```nginx
server {
    listen 80;
    server_name example.com;

    # Whitelist before blacklist
    allow 192.168.1.100;  # Trusted IP

    # Then apply blacklist
    include /path/to/blacklist.conf;

    # Deny all others not explicitly allowed
    # deny all;  # Optional
}
```

## Automatic Updates

These files are automatically regenerated daily when the blacklists are updated via the GitHub Actions workflow.

## Source

Generated from the blacklist files in the `blacklists/` directory by `blacklists_updater_nginx.sh`.

## See Also

- [IPTables/IPSet Format](../blacklists_iptables/README.md) - For firewall-level blocking
- [Text Format](../blacklists/README.md) - For custom integrations
- [Main Repository](https://github.com/C24Be/AS_Network_List) - Complete documentation
