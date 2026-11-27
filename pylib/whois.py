from __future__ import annotations

import functools
import json
import re
import time
from typing import Any, Dict

import requests

SEARCH_URL = "https://rest.db.ripe.net/search"
# RIPE blocks an IP for the rest of the day once it has returned 1,000 person or role objects;
# no-referenced leaves them, and the organisation, out of the answer.
NO_REFERENCED = "no-referenced"
NO_ENTRIES = "ERROR:101"
REFUSAL = re.compile(rb"ERROR:(?!101)\d+")
WHOIS_ATTEMPTS = 5
WHOIS_BACKOFF = 5
WHOIS_TIMEOUT = 30
OBJECT_TYPES = {
    "as-name": ("aut-num",),
    "netname": ("inetnum", "inet6num", "route", "route6"),
    "inetnum": ("inetnum",),
}
REQUIRED = {
    "aut-num": ("aut-num", "as-name"),
    "inetnum": ("inetnum", "netname"),
    "inet6num": ("inet6num", "netname"),
    "route": ("route", "origin"),
    "route6": ("route6", "origin"),
    "organisation": ("organisation", "org-name"),
}
TRANSIENT = (
    requests.ConnectionError,
    requests.Timeout,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.ContentDecodingError,
)

SESSION = requests.Session()

Body = Dict[str, Any]


class WhoisError(Exception):
    pass


def _body(raw: bytes) -> Body | None:
    try:
        body = json.loads(raw)
    except ValueError:
        return None
    return body if isinstance(body, dict) else None


def _errors(body: Body) -> list[str]:
    container = body.get("errormessages")
    messages = container.get("errormessage") if isinstance(container, dict) else None
    errors = []
    for message in messages if isinstance(messages, list) else []:
        if not isinstance(message, dict) or message.get("severity") != "Error":
            continue
        text = str(message.get("text", ""))
        for arg in message.get("args") or []:
            text = text.replace("%s", str(arg.get("value", "") if isinstance(arg, dict) else arg), 1)
        errors.append(" ".join(text.split()))
    return errors


def _is_attribute(attribute: object) -> bool:
    return (
        isinstance(attribute, dict)
        and isinstance(attribute.get("name"), str)
        and isinstance(attribute.get("value"), str)
    )


def _is_object(obj: object) -> bool:
    if not isinstance(obj, dict) or not isinstance(obj.get("type"), str):
        return False
    attributes = obj.get("attributes")
    items = attributes.get("attribute") if isinstance(attributes, dict) else None
    if not isinstance(items, list) or not all(_is_attribute(a) for a in items):
        return False
    names = {a["name"] for a in items if a["value"].strip()}
    return all(n in names for n in REQUIRED.get(obj["type"], (obj["type"],)))


def _objects(body: Body) -> list[Body] | None:
    container = body.get("objects")
    objects = container.get("object") if isinstance(container, dict) else None
    if not isinstance(objects, list) or not all(_is_object(o) for o in objects):
        return None
    return objects


def _fetch(params: dict[str, Any]) -> tuple[int, Body | None]:
    query = params["query-string"]
    for attempt in range(WHOIS_ATTEMPTS):
        try:
            with SESSION.get(
                SEARCH_URL,
                params=params,
                headers={"Accept": "application/json"},
                timeout=WHOIS_TIMEOUT,
                stream=True,
            ) as response:
                status = response.status_code
                try:
                    raw = response.content
                except TRANSIENT as exc:
                    if status >= 500:
                        raise
                    raise WhoisError(
                        f"query {query!r} failed: HTTP {status}: answer cut off, not retried"
                        f" since the lost part may be a refusal: {exc}"
                    ) from exc
                body = _body(raw)
        except TRANSIENT as exc:
            problem = str(exc)
        except requests.RequestException as exc:
            raise WhoisError(f"query {query!r} failed: {exc}") from exc
        else:
            if status >= 500:
                problem = f"HTTP {status}"
            elif status == 200 and (body is None or (_objects(body) is None and not _errors(body))):
                refusal = REFUSAL.search(raw)
                if refusal:
                    raise WhoisError(
                        f"query {query!r} refused: HTTP 200: malformed answer carrying {refusal.group().decode()}"
                    )
                problem = "malformed answer"
            else:
                return status, body
        if attempt == WHOIS_ATTEMPTS - 1:
            raise WhoisError(f"query {query!r} failed after {WHOIS_ATTEMPTS} attempts: {problem}")
        time.sleep(WHOIS_BACKOFF * 2 ** attempt)
    raise AssertionError("unreachable")


def _search(query: str, types: tuple[str, ...]) -> list[Body]:
    params = {"source": "RIPE", "query-string": query, "type-filter": list(types), "flags": NO_REFERENCED}
    status, body = _fetch(params)
    errors = _errors(body or {})
    if status == 404 and errors and all(e.startswith(NO_ENTRIES) for e in errors):
        return []
    # A search streams its answer, so an error found part-way arrives inside an HTTP 200.
    refusals = [e for e in errors if not e.startswith(NO_ENTRIES)]
    objects = _objects(body) if status == 200 and body is not None else None
    if status != 200 or refusals or objects is None:
        detail = "; ".join(refusals or errors) or "no error message"
        raise WhoisError(f"query {query!r} refused: HTTP {status}: {detail}")
    return [o for o in objects if o["type"] in types]


def _value(obj: Body, name: str) -> str | None:
    for attribute in obj.get("attributes", {}).get("attribute", []):
        if attribute["name"] == name:
            return str(attribute["value"]).strip()
    return None


@functools.lru_cache(maxsize=None)
def _org_name(handle: str) -> str | None:
    for obj in _search(handle, ("organisation",)):
        if (_value(obj, "organisation") or "").upper() == handle.upper():
            return _value(obj, "org-name")
    return None


def whois_query(query: str, get_field: str = "netname", get_org: bool = False) -> str | list[str]:
    """Return get_field of the RIPE Database object for query, with its org name if get_org.

    get_field "inetnum" returns every matching inetnum range; the others return one name,
    or "-no-description-" when RIPE has no such object.
    """
    types = OBJECT_TYPES.get(get_field)
    if types is None:
        raise ValueError(f"unsupported field {get_field!r}; expected one of {sorted(OBJECT_TYPES)}")
    objects = _search(query, types)
    if get_field == "inetnum":
        return [r for r in (_value(o, "inetnum") for o in objects) if r]

    named = [o for o in objects if _value(o, get_field) is not None]
    first = named[0] if named else {}
    name = _value(first, get_field) or "-no-description-"
    if not get_org:
        return name
    handles = (_value(o, "org") for o in [first, *(o for o in objects if o is not first)])
    handle = next((h for h in handles if h), None)
    org_name = (_org_name(handle) if handle else None) or "No org name found"
    return f"{name} ({org_name})"
