import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OK_AS = '#!/bin/sh\necho "# Networks announced by AS64496"\necho 192.0.2.0/24\necho 2001:db8::/32\n'
OK_NETNAME = '#!/bin/sh\necho "# Network name: TEST"\necho 198.51.100.0/24\n'
FAILING = '#!/bin/sh\necho 203.0.113.0/24\nexit 1\n'
OLD_LIST = "10.0.0.0/8\n"


class BlacklistsUpdaterTxtTests(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.root = Path(tmpdir.name)
        for name in ("blacklists_updater_txt.sh", "blacklists_updater_common.subr"):
            shutil.copy(REPO / name, self.root / name)
        for directory in ("auto", "lists", "blacklists"):
            (self.root / directory).mkdir()
        for name in ("all-ru-asn.txt", "all-ru-ipv4.txt", "ripe-ru-ipv4.txt"):
            (self.root / "auto" / name).write_text("no matching names here\n", encoding="utf-8")
        (self.root / "lists" / "ru-gov-netnames.txt").write_text("TEST\n", encoding="utf-8")
        for name in ("blacklist.txt", "blacklist-v4.txt", "blacklist-v6.txt"):
            (self.root / "blacklists" / name).write_text(OLD_LIST, encoding="utf-8")

    def run_updater(self, as_script, netname_script):
        for name, body in (("network_list_from_as.py", as_script), ("network_list_from_netname.py", netname_script)):
            path = self.root / name
            path.write_text(body, encoding="utf-8")
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return subprocess.run(
            ["sh", str(self.root / "blacklists_updater_txt.sh")],
            capture_output=True,
            text=True,
            check=False,
        )

    def published(self, name):
        return (self.root / "blacklists" / name).read_text(encoding="utf-8")

    def assert_lists_untouched(self):
        for name in ("blacklist.txt", "blacklist-v4.txt", "blacklist-v6.txt"):
            self.assertEqual(self.published(name), OLD_LIST)

    def test_as_lookup_failure_fails_and_keeps_the_lists(self):
        result = self.run_updater(FAILING, OK_NETNAME)
        self.assertNotEqual(result.returncode, 0)
        self.assert_lists_untouched()

    def test_netname_lookup_failure_fails_and_keeps_the_lists(self):
        result = self.run_updater(OK_AS, FAILING)
        self.assertNotEqual(result.returncode, 0)
        self.assert_lists_untouched()

    def test_success_with_no_name_matches_publishes_the_lists(self):
        result = self.run_updater(OK_AS, OK_NETNAME)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.published("blacklist.txt"), "192.0.2.0/24\n198.51.100.0/24\n2001:db8::/32\n")
        self.assertEqual(self.published("blacklist-v4.txt"), "192.0.2.0/24\n198.51.100.0/24\n")
        self.assertEqual(self.published("blacklist-v6.txt"), "2001:db8::/32\n")


if __name__ == "__main__":
    unittest.main()
