import json
import unittest
from unittest import mock

import requests
import urllib3

from pylib import whois
from pylib.whois import (
    SEARCH_URL,
    WHOIS_ATTEMPTS,
    WHOIS_TIMEOUT,
    WhoisError,
    whois_query,
)


def reply(status, body):
    response = requests.Response()
    response.status_code = status
    response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
    response.encoding = "utf-8"
    response._content_consumed = True
    return response


def broken(status):
    response = requests.Response()
    response.status_code = status
    response.raw = mock.Mock()
    response.raw.stream.side_effect = urllib3.exceptions.ProtocolError("Connection broken: IncompleteRead")
    return response


def rpsl(kind, *attributes):
    return {"type": kind, "attributes": {"attribute": [{"name": n, "value": v} for n, v in attributes]}}


def cut_off(status, body):
    def stream(*args, **kwargs):
        yield json.dumps(body).encode()
        raise urllib3.exceptions.ProtocolError("Connection broken: IncompleteRead")

    response = requests.Response()
    response.status_code = status
    response.raw = mock.Mock()
    response.raw.stream.side_effect = stream
    return response


def timed_out(status):
    response = broken(status)
    response.raw.stream.side_effect = urllib3.exceptions.ReadTimeoutError(None, None, "Read timed out.")
    return response


def without_value(obj, name):
    for attribute in obj["attributes"]["attribute"]:
        if attribute["name"] == name:
            del attribute["value"]
    return obj


def message(text, severity="Error"):
    return {"severity": severity, "text": text, "args": [{"value": "RIPE"}]}


def found(*objects, messages=()):
    body = {"objects": {"object": list(objects)}}
    if messages:
        body["errormessages"] = {"errormessage": list(messages)}
    return reply(200, body)


def refused(status, text="ERROR:201: access denied for %s"):
    return reply(status, {"errormessages": {"errormessage": [message(text)]}})


def no_entries():
    return refused(404, "ERROR:101: no entries found\n\nNo entries found in source %s.\n")


INETNUM_ATTRS = (("inetnum", "192.0.2.0 - 192.0.2.255"), ("netname", "TEST"))
INETNUM = rpsl("inetnum", *INETNUM_ATTRS)
AUT_NUM = rpsl("aut-num", ("aut-num", "AS64496"), ("as-name", "TEST-AS"), ("org", "ORG-TEST1-RIPE"))
AUT_NUM_NO_ORG = rpsl("aut-num", ("aut-num", "AS64497"), ("as-name", "BARE-AS"))
ORGANISATION = rpsl("organisation", ("organisation", "ORG-TEST1-RIPE"), ("org-name", "Test LLC"))
NET_INETNUM = rpsl("inetnum", ("inetnum", "192.0.2.0 - 192.0.2.255"), ("netname", "TEST-NET"), ("org", "ORG-NET1-RIPE"))
NET_ROUTE = rpsl("route", ("route", "192.0.2.0/24"), ("origin", "AS64496"), ("org", "ORG-ROUTE1-RIPE"))
NET_ORGANISATION = rpsl("organisation", ("organisation", "ORG-NET1-RIPE"), ("org-name", "Net: Holding LLC"))
INET6NUM = rpsl("inet6num", ("inet6num", "2001:db8::/32"), ("netname", "TEST6-NET"))


class WhoisQueryTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("pylib.whois.time.sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)
        whois._org_name.cache_clear()

    def run_query(self, answers, *args):
        with mock.patch.object(whois.SESSION, "get", side_effect=answers) as get:
            return whois_query(*args), get

    def params(self, get, call=0):
        return get.call_args_list[call].kwargs["params"]

    def test_returns_inetnums_as_json_with_a_timeout(self):
        result, get = self.run_query([found(INETNUM)], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        self.assertEqual(get.call_args.args, (SEARCH_URL,))
        self.assertEqual(get.call_args.kwargs["timeout"], WHOIS_TIMEOUT)
        self.assertEqual(get.call_args.kwargs["headers"], {"Accept": "application/json"})
        self.assertIs(get.call_args.kwargs["stream"], True)

    def test_queries_skip_contact_objects(self):
        _, get = self.run_query([found(INETNUM)], "TEST", "inetnum")
        self.assertEqual(
            self.params(get),
            {"source": "RIPE", "query-string": "TEST", "type-filter": ["inetnum"], "flags": "no-referenced"},
        )

    def test_type_filter_follows_the_field(self):
        for field, types in (
            ("as-name", ["aut-num"]),
            ("netname", ["inetnum", "inet6num", "route", "route6"]),
            ("inetnum", ["inetnum"]),
        ):
            with self.subTest(field=field):
                _, get = self.run_query([no_entries()], "TEST", field)
                self.assertEqual(self.params(get)["type-filter"], types)

    def test_unsupported_field_is_rejected(self):
        with self.assertRaises(ValueError):
            whois_query("TEST", "descr")

    def test_transient_failures_are_retried(self):
        for failure in (
            requests.ConnectionError("reset"),
            requests.Timeout("timed out"),
            requests.exceptions.ChunkedEncodingError("broken transfer"),
            reply(503, b""),
            broken(503),
            reply(200, b'{"objects": {"object": ['),
            reply(200, b""),
            reply(200, {}),
            reply(200, {"objects": {"object": [{"type": "inetnum"}]}}),
            reply(200, {"objects": {"object": [{"type": "inetnum", "attributes": {"attribute": ["inetnum"]}}]}}),
            reply(200, {"objects": {"object": [rpsl("inetnum", ("inetnum", None), ("netname", "TEST"))]}}),
            reply(200, {"objects": {"object": [rpsl("inetnum", ("netname", "TEST"))]}}),
            reply(200, {"objects": {"object": [rpsl("aut-num", ("aut-num", "AS64496"))]}}),
            reply(200, {"objects": {"object": [rpsl("inetnum")]}}),
            reply(200, {"objects": {"object": [without_value(rpsl("inetnum", *INETNUM_ATTRS, ("org", "ORG-X")), "org")]}}),
            reply(200, {"objects": {"object": [rpsl("inetnum", ("inetnum", ""), ("netname", "TEST"))]}}),
            reply(200, {"objects": {"object": [rpsl("inetnum", ("inetnum", "192.0.2.0 - 192.0.2.255"), ("netname", " "))]}}),
        ):
            with self.subTest(failure=failure):
                self.sleep.reset_mock()
                result, get = self.run_query([failure, found(INETNUM)], "TEST", "inetnum")
                self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
                self.assertEqual(get.call_count, 2)
                self.sleep.assert_called_once()

    def test_answer_cut_off_mid_transfer_is_not_retried(self):
        denied = {"errormessages": {"errormessage": [message("ERROR:201: access denied for %s")]}}
        for status, answer in (
            (403, broken(403)),
            (429, broken(429)),
            (404, broken(404)),
            (200, broken(200)),
            (200, cut_off(200, denied)),
            (200, cut_off(200, {"objects": {"object": [INETNUM]}})),
            (200, timed_out(200)),
        ):
            with self.subTest(status=status, answer=answer.raw.stream.side_effect):
                with mock.patch.object(whois.SESSION, "get", side_effect=[answer]) as get:
                    with self.assertRaisesRegex(WhoisError, f"HTTP {status}: answer cut off"):
                        whois_query("AS0", "as-name", True)
                self.assertEqual(get.call_count, 1)

    def test_malformed_answer_carrying_a_refusal_is_not_retried(self):
        with mock.patch.object(whois.SESSION, "get", side_effect=[reply(200, b"<p>ERROR:201: access denied</p>")]) as get:
            with self.assertRaisesRegex(WhoisError, "HTTP 200: malformed answer carrying ERROR:201"):
                whois_query("TEST", "inetnum")
        self.assertEqual(get.call_count, 1)

    def test_malformed_answer_fails_after_retries(self):
        answers = [reply(200, {}) for _ in range(WHOIS_ATTEMPTS)]
        with mock.patch.object(whois.SESSION, "get", side_effect=answers) as get:
            with self.assertRaisesRegex(WhoisError, "malformed answer"):
                whois_query("TEST", "inetnum")
        self.assertEqual(get.call_count, WHOIS_ATTEMPTS)

    def test_gives_up_with_whois_error(self):
        failures = [requests.ConnectionError("reset") for _ in range(WHOIS_ATTEMPTS)]
        with mock.patch.object(whois.SESSION, "get", side_effect=failures) as get:
            with self.assertRaisesRegex(WhoisError, f"after {WHOIS_ATTEMPTS} attempts"):
                whois_query("TEST", "inetnum")
        self.assertEqual(get.call_count, WHOIS_ATTEMPTS)

    def test_other_request_errors_raise_without_retrying(self):
        with mock.patch.object(whois.SESSION, "get", side_effect=[requests.exceptions.InvalidURL("bad")]) as get:
            with self.assertRaises(WhoisError):
                whois_query("TEST", "inetnum")
        self.assertEqual(get.call_count, 1)

    def test_no_entries_is_an_empty_result_not_a_failure(self):
        result, get = self.run_query([no_entries()], "TEST", "inetnum")
        self.assertEqual(result, [])
        self.assertEqual(get.call_count, 1)

    def test_no_entries_keeps_the_description_placeholder(self):
        result, _ = self.run_query([no_entries()], "AS0", "as-name", True)
        self.assertEqual(result, "-no-description- (No org name found)")

    def test_query_limit_raises_without_retrying(self):
        for status in (403, 429):
            with self.subTest(status=status):
                with mock.patch.object(whois.SESSION, "get", side_effect=[refused(status)]) as get:
                    with self.assertRaisesRegex(WhoisError, f"HTTP {status}: ERROR:201: access denied for RIPE"):
                        whois_query("AS0", "as-name", True)
                self.assertEqual(get.call_count, 1)

    def test_error_inside_a_streamed_answer_raises(self):
        error = message("ERROR:201: access denied for %s")
        for answer in (found(INETNUM, messages=[error]), reply(200, {"errormessages": {"errormessage": [error]}})):
            with self.subTest(answer=answer.content[:20]):
                with mock.patch.object(whois.SESSION, "get", side_effect=[answer]) as get:
                    with self.assertRaisesRegex(WhoisError, "HTTP 200: ERROR:201"):
                        whois_query("TEST", "inetnum")
                self.assertEqual(get.call_count, 1)

    def test_warning_is_not_a_failure(self):
        answer = found(INETNUM, messages=[message("WARNING:902: useless IP flag passed", "Warning")])
        result, _ = self.run_query([answer], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])

    def test_other_client_errors_raise(self):
        for answer in (refused(400, "ERROR:105: invalid query"), reply(404, b"<html>not found</html>")):
            with self.subTest(status=answer.status_code):
                with mock.patch.object(whois.SESSION, "get", side_effect=[answer]) as get:
                    with self.assertRaisesRegex(WhoisError, f"HTTP {answer.status_code}"):
                        whois_query("TEST", "inetnum")
                self.assertEqual(get.call_count, 1)

    def test_org_name_is_read_from_the_org_handle(self):
        result, get = self.run_query([found(AUT_NUM), found(ORGANISATION)], "AS64496", "as-name", True)
        self.assertEqual(result, "TEST-AS (Test LLC)")
        self.assertEqual(
            self.params(get, 1),
            {
                "source": "RIPE",
                "query-string": "ORG-TEST1-RIPE",
                "type-filter": ["organisation"],
                "flags": "no-referenced",
            },
        )
        self.assertEqual(get.call_count, 2)

    def test_org_lookup_is_cached(self):
        answers = [found(AUT_NUM), found(ORGANISATION), found(AUT_NUM)]
        with mock.patch.object(whois.SESSION, "get", side_effect=answers) as get:
            whois_query("AS64496", "as-name", True)
            result = whois_query("AS64496", "as-name", True)
        self.assertEqual(result, "TEST-AS (Test LLC)")
        self.assertEqual(get.call_count, 3)

    def test_no_org_handle_makes_no_org_lookup(self):
        result, get = self.run_query([found(AUT_NUM_NO_ORG)], "AS64497", "as-name", True)
        self.assertEqual(result, "BARE-AS (No org name found)")
        self.assertEqual(get.call_count, 1)

    def test_inetnum_lookup_makes_no_org_lookup(self):
        result, get = self.run_query([found(NET_INETNUM)], "TEST-NET", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        self.assertEqual(get.call_count, 1)

    def test_network_description_reads_the_inetnum_org_and_keeps_colons(self):
        answers = [found(NET_ROUTE, NET_INETNUM), found(NET_ORGANISATION)]
        result, get = self.run_query(answers, "192.0.2.0/24", "netname", True)
        self.assertEqual(result, "TEST-NET (Net: Holding LLC)")
        self.assertEqual(self.params(get, 0)["query-string"], "192.0.2.0/24")
        self.assertEqual(self.params(get, 1)["query-string"], "ORG-NET1-RIPE")

    def test_network_without_an_org_takes_the_route_org(self):
        bare = rpsl("inetnum", ("inetnum", "192.0.2.0 - 192.0.2.255"), ("netname", "TEST-NET"))
        route = rpsl("route", ("route", "192.0.2.0/24"), ("origin", "AS64496"), ("org", "ORG-NET1-RIPE"))
        result, get = self.run_query([found(bare, route), found(NET_ORGANISATION)], "192.0.2.0/24", "netname", True)
        self.assertEqual(result, "TEST-NET (Net: Holding LLC)")
        self.assertEqual(self.params(get, 1)["query-string"], "ORG-NET1-RIPE")

    def test_ipv6_network_description(self):
        result, _ = self.run_query([found(INET6NUM)], "2001:db8::/32", "netname", True)
        self.assertEqual(result, "TEST6-NET (No org name found)")

    def test_refused_org_lookup_raises(self):
        with mock.patch.object(whois.SESSION, "get", side_effect=[found(AUT_NUM), refused(429)]):
            with self.assertRaisesRegex(WhoisError, "ORG-TEST1-RIPE.*HTTP 429"):
                whois_query("AS64496", "as-name", True)


if __name__ == "__main__":
    unittest.main()
