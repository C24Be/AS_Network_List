import contextlib
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

import network_list_from_as
import network_list_from_netname
from pylib.whois import WhoisError


class FlakyRipestat(BaseHTTPRequestHandler):
    failures_left = 0
    requests_seen = 0

    def do_GET(self):
        cls = type(self)
        cls.requests_seen += 1
        if cls.failures_left > 0:
            cls.failures_left -= 1
            self.send_response(500)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = json.dumps({"data": {"prefixes": [{"prefix": "192.0.2.0/24"}]}}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class NetworkListFromAsTests(unittest.TestCase):
    def setUp(self):
        FlakyRipestat.requests_seen = 0
        server = HTTPServer(("127.0.0.1", 0), FlakyRipestat)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = f"http://127.0.0.1:{server.server_port}/?resource={{asn}}"
        for patcher in (
            mock.patch.object(network_list_from_as, "ANNOUNCED_PREFIXES_URL", url),
            mock.patch.object(network_list_from_as, "SESSION", network_list_from_as.build_session(backoff_factor=0)),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_main(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = network_list_from_as.main(["-q", "AS64496"])
        return code, out.getvalue(), err.getvalue()

    def test_server_errors_are_retried(self):
        FlakyRipestat.failures_left = 2
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(out, "192.0.2.0/24\n")
        self.assertEqual(FlakyRipestat.requests_seen, 3)

    def test_persistent_server_error_fails_the_script(self):
        FlakyRipestat.failures_left = 100
        code, out, err = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("ERROR: failed to fetch ASN data", err)

    def test_whois_failure_fails_the_script(self):
        err = io.StringIO()
        with mock.patch.object(network_list_from_as, "whois_query", side_effect=WhoisError("reset")):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = network_list_from_as.main(["AS64496"])
        self.assertEqual(code, 1)
        self.assertIn("ERROR: failed to fetch ASN data", err.getvalue())


class NetworkListFromNetnameTests(unittest.TestCase):
    def run_main(self, whois):
        with tempfile.TemporaryDirectory() as tmpdir:
            names = Path(tmpdir) / "names.txt"
            names.write_text("FIRST\nSECOND\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(network_list_from_netname, "whois_query", whois):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = network_list_from_netname.main([str(names)])
        return code, out.getvalue(), err.getvalue()

    def test_failure_on_a_later_name_fails_the_script(self):
        whois = mock.Mock(side_effect=[["192.0.2.0 - 192.0.2.255"], WhoisError("reset")])
        code, out, err = self.run_main(whois)
        self.assertEqual(code, 1)
        self.assertIn("192.0.2.0/24", out)
        self.assertIn("ERROR: failed to fetch netname data", err)

    def test_name_without_objects_is_skipped(self):
        whois = mock.Mock(side_effect=[[], ["192.0.2.0 - 192.0.2.255"]])
        code, out, _ = self.run_main(whois)
        self.assertEqual(code, 0)
        self.assertNotIn("FIRST", out)
        self.assertIn("# Network name: SECOND", out)

    def test_lookup_skips_contact_objects(self):
        whois = mock.Mock(return_value=[])
        self.run_main(whois)
        whois.assert_any_call("-r FIRST", "inetnum")


if __name__ == "__main__":
    unittest.main()
