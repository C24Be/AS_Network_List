import unittest
from unittest import mock

from pylib.whois import WHOIS_ATTEMPTS, WHOIS_TIMEOUT, WhoisError, whois_query

HIT = b"% RIPE header\n\ninetnum:        192.0.2.0 - 192.0.2.255\nnetname:        TEST\n"
NO_ENTRIES = b"% RIPE header\n\n%ERROR:101: no entries found\n%\n"
DENIED = b"% RIPE header\n\n%ERROR:201: access denied for 192.0.2.1\n"


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

    def test_refused_description_lookup_keeps_the_placeholder(self):
        result, sock = self.run_query([answers(DENIED)], "AS0", "as-name", True)
        self.assertEqual(result, "-no-description- (No org name found)")
        self.assertEqual(sock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
