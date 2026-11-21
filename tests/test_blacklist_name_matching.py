import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BlacklistNameMatchingTests(unittest.TestCase):
    def assert_name_match(self, record, expected, pattern="BLACK_NAMES"):
        result = subprocess.run(
            [
                "sh",
                "-c",
                'SCRIPT_DIR=.; . ./blacklists_updater_common.subr; '
                'case "$1" in BLACK_NAMES) grep -iE "$BLACK_NAMES";; '
                'VK_NAME_PATTERN) grep -iE "$VK_NAME_PATTERN";; esac',
                "sh",
                pattern,
            ],
            input=record + "\n",
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertEqual(result.returncode == 0, expected, record)

    def test_vk_as_matches_as_a_complete_name(self):
        for record in (
            "AS64512 VK-AS (Example Network)",
            "AS64512 vk-as (Example Network)",
            "VK-AS",
            "AS64512 VK-AS",
            "(VK-AS)",
            "AS64512 VKAS",
            "AS64512 VKONTAKTE-SPB-AS",
            "AS64512 VKCOMPANY-CLOUD-AS",
            "AS64512 Example (VK LLC)",
            "AS64512 Example (LLC\tVK)",
            "192.0.2.0/24 RU-VKONTAKTE-20080703",
        ):
            for pattern in ("BLACK_NAMES", "VK_NAME_PATTERN"):
                with self.subTest(record=record, pattern=pattern):
                    self.assert_name_match(record, True, pattern)

    def test_vk_as_does_not_match_inside_other_names(self):
        for record in (
            "AS43720 TVK-AS (MTS OJSC)",
            "AS43038 TVK-AS (MTS PJSC)",
            "AS64512 OTHER-VK-AS (Example Network)",
            "AS64512 VK-AS-OTHER (Example Network)",
            "AS64512 VK-AS_OTHER (Example Network)",
            "AS64512 VK-AS123 (Example Network)",
            "AS29043 VKE-AS (Other owner)",
            "192.0.2.0/24 TVKAS (TVK LLC)",
            "192.0.2.0/24 TVK-AS (LLC TVK)",
            "192.0.2.0/24 TVKCOMPANY-AS",
            "192.0.2.0/24 TVKONTAKTE-SPB-AS",
        ):
            for pattern in ("BLACK_NAMES", "VK_NAME_PATTERN"):
                with self.subTest(record=record, pattern=pattern):
                    self.assert_name_match(record, False, pattern)

    def test_other_blacklist_terms_still_match(self):
        for record in (
            "AS47764 VK-AS (LLC VK)",
            "AS64512 TVK-AS (FGUP Example)",
            "AS64512 VKONTAKTE-SPB-AS (Example Network)",
        ):
            with self.subTest(record=record):
                self.assert_name_match(record, True)


class VkBlacklistTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.blacklists = self.root / "blacklists"
        self.blacklists.mkdir()
        (self.root / "auto").mkdir()
        (self.root / "auto" / "all-ru-ipv4.txt").write_text(
            "192.0.2.0/24 LLC VK\n"
            "154.90.70.0/24 LLC VK\n"
            "198.51.100.0/24 LLC VK Cloud Solutions VK Hosting\n"
            "203.0.113.0/24 unrelated\n",
            encoding="utf-8",
        )
        (self.root / "auto" / "all-ru-ipv6.txt").write_text(
            "2001:db8::/32 LLC VK\n", encoding="utf-8"
        )

    def run_builder(self, lookup, extra_lookup="exit 2\n"):
        generator = self.root / "network_list_from_as.py"
        generator.write_text(
            '#!/bin/sh\n[ "$#" -eq 2 ] && [ "$1" = --quiet ] || exit 2\n'
            'printf "%s\\n" "$2" >> "$(dirname "$0")/lookups"\n'
            f'case "$2" in\nAS47764) {lookup};;\nAS64512) {extra_lookup};;\n*) exit 2;;\nesac\n',
            encoding="utf-8",
        )
        generator.chmod(0o700)
        return subprocess.run(
            [
                "sh",
                "-c",
                'SCRIPT_DIR=$1; . "$2"; build_vk_name_blacklists',
                "sh",
                str(self.root),
                str(REPO_ROOT / "blacklists_updater_common.subr"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_announced_prefixes_are_merged_and_deduplicated(self):
        result = self.run_builder(
            "printf '%s\\n' 154.90.70.0/24 154.90.71.0/24 2001:db8:1::/48\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        v4 = "154.90.70.0/24\n154.90.71.0/24\n192.0.2.0/24\n"
        v6 = "2001:db8:1::/48\n2001:db8::/32\n"
        for name, expected in (
            ("blacklist-vk.txt", v4 + v6),
            ("blacklist-vk-v4.txt", v4),
            ("blacklist-vk-v6.txt", v6),
        ):
            with self.subTest(name=name):
                self.assertEqual((self.blacklists / name).read_text(), expected)

    def test_failed_or_empty_lookup_preserves_published_lists(self):
        for name in ("blacklist-vk.txt", "blacklist-vk-v4.txt", "blacklist-vk-v6.txt"):
            (self.blacklists / name).write_text("old\n", encoding="utf-8")

        for lookup in ("echo 154.90.70.0/24\nexit 1\n", "exit 0\n"):
            with self.subTest(lookup=lookup):
                result = self.run_builder(lookup)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("failed to load announced prefixes for AS47764", result.stderr)
                self.assertCountEqual(
                    [path.read_text() for path in self.blacklists.iterdir()],
                    ["old\n", "old\n", "old\n"],
                )

    def test_only_named_vk_asns_are_resolved_and_deduplicated(self):
        (self.root / "auto" / "all-ru-asn.txt").write_text(
            "AS47764 VK-AS (LLC VK)\n"
            "AS64512 VKAS (VK LLC)\n"
            "as64512 VKONTAKTE-SPB-AS\n"
            "AS43720 TVK-AS (MTS OJSC)\n"
            "AS29043 VKE-AS (Other owner)\n",
            encoding="utf-8",
        )
        result = self.run_builder("echo 154.90.70.0/24\n", "echo 203.0.113.0/24\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "lookups").read_text().splitlines(), ["AS47764", "AS64512"])
        self.assertIn("203.0.113.0/24", (self.blacklists / "blacklist-vk-v4.txt").read_text().splitlines())

    def test_failed_named_vk_asn_lookup_preserves_published_lists(self):
        (self.root / "auto" / "all-ru-asn.txt").write_text("AS64512 (VK LLC)\n", encoding="utf-8")
        names = ("blacklist-vk.txt", "blacklist-vk-v4.txt", "blacklist-vk-v6.txt")
        for name in names:
            (self.blacklists / name).write_text("old\n", encoding="utf-8")
        result = self.run_builder("echo 154.90.70.0/24\n", "echo 203.0.113.0/24\nexit 1\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed to load announced prefixes for AS64512", result.stderr)
        self.assertEqual(sorted(p.name for p in self.blacklists.iterdir()), sorted(names))
        for name in names:
            self.assertEqual((self.blacklists / name).read_text(), "old\n")


if __name__ == "__main__":
    unittest.main()
