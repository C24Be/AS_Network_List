import ipaddress

def convert_to_cidr(ip_range):
    start_ip, end_ip = ip_range.split(' - ')
    start_ip = ipaddress.IPv4Address(start_ip)
    end_ip = ipaddress.IPv4Address(end_ip)
    cidrs = ipaddress.summarize_address_range(start_ip, end_ip)
    return [str(cidr) for cidr in cidrs]
