import socket

def whois_query(query, get_field="netname", get_org=False):

    whois_server = "whois.ripe.net"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((whois_server, 43))

    query = f"{query}\r\n"
    s.send(query.encode())

    response = ''
    while True:
        data = s.recv(4096)
        try:
            response += data.decode('utf-8')
        except:
            response += data.decode('latin-1')
        if not data:
            break
    s.close()

    org_name = None
    if get_field == "inetnum":
        basic_name = []
    else:
        basic_name = None
    for line in response.split('\n'):
        if line.startswith('org-name' + ':'):
            org_name = line.split(':')[1].strip()
        if line.startswith(get_field + ':'):
            if get_field == "inetnum":
                basic_name.append(line.split(':')[1].strip())
            else:
                basic_name = line.split(':')[1].strip()

    if basic_name is None:
        basic_name = '-no-description-'

    if org_name is None:
        org_name = 'No org name found'

    if get_org is True:
        return str(basic_name) + ' (' + org_name + ')'
    else:
        return basic_name
