import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BlacklistNameMatchingTests(unittest.TestCase):
    def assert_name_match(self, record, expected):
        result = subprocess.run(
            [
                "sh",
                "-c",
                'SCRIPT_DIR=.; . ./blacklists_updater_common.subr; grep -iE "$BLACK_NAMES"',
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
        ):
            with self.subTest(record=record):
                self.assert_name_match(record, True)

    def test_vk_as_does_not_match_inside_other_names(self):
        for record in (
            "AS43720 TVK-AS (MTS OJSC)",
            "AS43038 TVK-AS (MTS PJSC)",
            "AS64512 OTHER-VK-AS (Example Network)",
            "AS64512 VK-AS-OTHER (Example Network)",
            "AS64512 VK-AS_OTHER (Example Network)",
            "AS64512 VK-AS123 (Example Network)",
        ):
            with self.subTest(record=record):
                self.assert_name_match(record, False)

    def test_other_blacklist_terms_still_match(self):
        for record in (
            "AS47764 VK-AS (LLC VK)",
            "AS64512 TVK-AS (FGUP Example)",
            "AS64512 VKONTAKTE-SPB-AS (Example Network)",
        ):
            with self.subTest(record=record):
                self.assert_name_match(record, True)


if __name__ == "__main__":
    unittest.main()
