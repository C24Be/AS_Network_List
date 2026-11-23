import unittest
from unittest import mock

from pylib import whois
from pylib.whois import WHOIS_ATTEMPTS, WHOIS_TIMEOUT, WhoisError, whois_query

HIT = b"% RIPE header\n\ninetnum:        192.0.2.0 - 192.0.2.255\nnetname:        TEST\n"
NO_ENTRIES = b"% RIPE header\n\n%ERROR:101: no entries found\n%\n"
DENIED = b"% RIPE header\n\n%ERROR:201: access denied for 192.0.2.1\n"
AUT_NUM = b"aut-num:        AS64496\nas-name:        TEST-AS\norg:            ORG-TEST1-RIPE\n"
AUT_NUM_NO_ORG = b"aut-num:        AS64497\nas-name:        BARE-AS\n"
ORGANISATION = b"organisation:   ORG-TEST1-RIPE\norg-name:       Test LLC\n"
NET_AND_ROUTE = (
    b"inetnum:        192.0.2.0 - 192.0.2.255\nnetname:        TEST-NET\norg:            ORG-NET1-RIPE\n\n"
    b"route:          192.0.2.0/24\norigin:         AS64496\norg:            ORG-ROUTE1-RIPE\n"
)
NET_ORGANISATION = b"organisation:   ORG-NET1-RIPE\norg-name:       Net LLC\n"


def connection(*recv_results):
    conn = mock.MagicMock()
    conn.__enter__.return_value = conn
    conn.recv.side_effect = list(recv_results)
    return conn


def answers(data):
    return connection(data, b"")


def reset():
    return connection(ConnectionResetError(104, "Connection reset by peer"))


class WhoisQueryTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("pylib.whois.time.sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)
        whois._org_name.cache_clear()

    def run_query(self, connections, *args):
        with mock.patch("pylib.whois.socket.socket", side_effect=connections) as sock:
            return whois_query(*args), sock

    def test_returns_inetnums_and_sets_a_timeout(self):
        conn = answers(HIT)
        result, _ = self.run_query([conn], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        conn.settimeout.assert_called_once_with(WHOIS_TIMEOUT)

    def test_connection_reset_is_retried(self):
        result, sock = self.run_query([reset(), answers(HIT)], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        self.assertEqual(sock.call_count, 2)
        self.sleep.assert_called_once()

    def test_reset_during_a_partial_answer_is_retried(self):
        partial = connection(b"inetnum: 198.51.100.0 - 198.51.100.255\n", ConnectionResetError(104, "reset"))
        result, _ = self.run_query([partial, answers(HIT)], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])

    def test_empty_answer_is_retried(self):
        result, sock = self.run_query([answers(b""), answers(HIT)], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        self.assertEqual(sock.call_count, 2)

    def test_gives_up_with_whois_error(self):
        connections = [reset() for _ in range(WHOIS_ATTEMPTS)]
        with mock.patch("pylib.whois.socket.socket", side_effect=connections) as sock:
            with self.assertRaises(WhoisError):
                whois_query("TEST", "inetnum")
        self.assertEqual(sock.call_count, WHOIS_ATTEMPTS)

    def test_no_entries_is_an_empty_result_not_a_failure(self):
        result, sock = self.run_query([answers(NO_ENTRIES)], "TEST", "inetnum")
        self.assertEqual(result, [])
        self.assertEqual(sock.call_count, 1)

    def test_no_entries_keeps_the_description_placeholder(self):
        result, _ = self.run_query([answers(NO_ENTRIES)], "AS0", "as-name", True)
        self.assertEqual(result, "-no-description- (No org name found)")

    def test_refused_query_raises_without_retrying(self):
        with mock.patch("pylib.whois.socket.socket", side_effect=[answers(DENIED)]) as sock:
            with self.assertRaisesRegex(WhoisError, "ERROR:201"):
                whois_query("TEST", "inetnum")
        self.assertEqual(sock.call_count, 1)

    def test_refused_description_lookup_raises_without_retrying(self):
        with mock.patch("pylib.whois.socket.socket", side_effect=[answers(DENIED)]) as sock:
            with self.assertRaisesRegex(WhoisError, "ERROR:201"):
                whois_query("AS0", "as-name", True)
        self.assertEqual(sock.call_count, 1)

    def test_queries_skip_contact_objects(self):
        conn = answers(HIT)
        self.run_query([conn], "TEST", "inetnum")
        conn.sendall.assert_called_once_with(b"-r TEST\r\n")

    def test_no_referenced_flag_is_not_repeated(self):
        conn = answers(HIT)
        self.run_query([conn], "-r TEST", "inetnum")
        conn.sendall.assert_called_once_with(b"-r TEST\r\n")

    def test_org_name_is_read_from_the_org_handle(self):
        org = answers(ORGANISATION)
        result, sock = self.run_query([answers(AUT_NUM), org], "AS64496", "as-name", True)
        self.assertEqual(result, "TEST-AS (Test LLC)")
        org.sendall.assert_called_once_with(b"-r ORG-TEST1-RIPE\r\n")
        self.assertEqual(sock.call_count, 2)

    def test_org_lookup_is_cached(self):
        connections = [answers(AUT_NUM), answers(ORGANISATION), answers(AUT_NUM)]
        with mock.patch("pylib.whois.socket.socket", side_effect=connections) as sock:
            whois_query("AS64496", "as-name", True)
            result = whois_query("AS64496", "as-name", True)
        self.assertEqual(result, "TEST-AS (Test LLC)")
        self.assertEqual(sock.call_count, 3)

    def test_no_org_handle_makes_no_org_lookup(self):
        result, sock = self.run_query([answers(AUT_NUM_NO_ORG)], "AS64497", "as-name", True)
        self.assertEqual(result, "BARE-AS (No org name found)")
        self.assertEqual(sock.call_count, 1)

    def test_inetnum_lookup_makes_no_org_lookup(self):
        result, sock = self.run_query([answers(HIT + b"org:            ORG-TEST1-RIPE\n")], "TEST", "inetnum")
        self.assertEqual(result, ["192.0.2.0 - 192.0.2.255"])
        self.assertEqual(sock.call_count, 1)

    def test_network_description_reads_the_inetnum_org(self):
        lookup, org = answers(NET_AND_ROUTE), answers(NET_ORGANISATION)
        result, sock = self.run_query([lookup, org], "192.0.2.0/24", "netname", True)
        self.assertEqual(result, "TEST-NET (Net LLC)")
        lookup.sendall.assert_called_once_with(b"-r 192.0.2.0/24\r\n")
        org.sendall.assert_called_once_with(b"-r ORG-NET1-RIPE\r\n")
        self.assertEqual(sock.call_count, 2)

    def test_refused_org_lookup_raises(self):
        with mock.patch("pylib.whois.socket.socket", side_effect=[answers(AUT_NUM), answers(DENIED)]):
            with self.assertRaisesRegex(WhoisError, "ERROR:201"):
                whois_query("AS64496", "as-name", True)


if __name__ == "__main__":
    unittest.main()
