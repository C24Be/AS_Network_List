import functools
import socket
import time

WHOIS_SERVER = "whois.ripe.net"
# RIPE blocks an IP for the rest of the day once it has returned 1,000 person or role objects;
# -r (--no-referenced) leaves them, and the organisation, out of the answer.
NO_REFERENCED = "-r"
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


def _no_referenced(query):
    if query.split(maxsplit=1)[:1] == [NO_REFERENCED]:
        return query
    return f"{NO_REFERENCED} {query}"


def _served(query):
    response = _fetch_with_retries(query)
    for line in response.split('\n'):
        # RIPE answers %ERROR:101 when nothing matches; any other %ERROR means the query was not served.
        if line.startswith('%ERROR:') and not line.startswith('%ERROR:101'):
            raise WhoisError(f"query {query!r} refused: {line.strip()}")
    return response


@functools.lru_cache(maxsize=None)
def _org_name(handle):
    for line in _served(_no_referenced(handle)).split('\n'):
        if line.startswith('org-name' + ':'):
            return line.split(':')[1].strip()
    return None


def whois_query(query, get_field="netname", get_org=False):

    response = _served(_no_referenced(query))

    org_handle = None
    if get_field == "inetnum":
        basic_name = []
    else:
        basic_name = None
    for line in response.split('\n'):
        if line.startswith('org' + ':') and org_handle is None:
            org_handle = line.split(':')[1].strip()
        if line.startswith(get_field + ':'):
            if get_field == "inetnum":
                basic_name.append(line.split(':')[1].strip())
            else:
                basic_name = line.split(':')[1].strip()

    if basic_name is None:
        basic_name = '-no-description-'

    org_name = _org_name(org_handle) if get_org and org_handle else None
    if org_name is None:
        org_name = 'No org name found'

    if get_org is True:
        return str(basic_name) + ' (' + org_name + ')'
    else:
        return basic_name
