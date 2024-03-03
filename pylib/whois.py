import socket

def whois_query(query, get_field="netname"):

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

    for line in response.split('\n'):
        if line.startswith(get_field + ':'):
            return line.strip()

    return None
