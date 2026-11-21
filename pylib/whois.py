import socket
import time

WHOIS_SERVER = "whois.ripe.net"
WHOIS_ATTEMPTS = 5
WHOIS_BACKOFF = 5
WHOIS_TIMEOUT = 30


class WhoisError(Exception):
    pass


def _fetch(query):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(WHOIS_TIMEOUT)
        s.connect((WHOIS_SERVER, 43))
        s.sendall(f"{query}\r\n".encode())

        response = ''
        while True:
            data = s.recv(4096)
            try:
                response += data.decode('utf-8')
            except UnicodeDecodeError:
                response += data.decode('latin-1')
            if not data:
                break

    if not response:
        raise ConnectionError("empty response")
    return response


def _fetch_with_retries(query):
    for attempt in range(WHOIS_ATTEMPTS):
        try:
            return _fetch(query)
        except OSError as exc:
            if attempt == WHOIS_ATTEMPTS - 1:
                raise WhoisError(f"query {query!r} failed after {WHOIS_ATTEMPTS} attempts: {exc}") from exc
            time.sleep(WHOIS_BACKOFF * 2 ** attempt)


def whois_query(query, get_field="netname", get_org=False):

    response = _fetch_with_retries(query)

    org_name = None
    if get_field == "inetnum":
        basic_name = []
    else:
        basic_name = None
    for line in response.split('\n'):
        # RIPE answers %ERROR:101 when nothing matches; any other %ERROR means the query was not served.
        if get_field == "inetnum" and line.startswith('%ERROR:') and not line.startswith('%ERROR:101'):
            raise WhoisError(f"query {query!r} refused: {line.strip()}")
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
