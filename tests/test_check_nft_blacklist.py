import tempfile
import unittest
from pathlib import Path

from check_nft_blacklist import check_ip_in_blacklist, parse_nft_config
from generate_nft_blacklist import make_nft_config


class CheckNftBlacklistTests(unittest.TestCase):
    def test_vk_sets_are_parsed(self):
        config = make_nft_config(["87.240.128.0/18"], [], usage_profile="vk_forward")

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "blacklist-vk-v4.nft"
            config_path.write_text(config, encoding="utf-8")

            v4_prefixes, v6_prefixes = parse_nft_config(config_path)
            blocked, prefix = check_ip_in_blacklist("87.240.128.1", v4_prefixes, v6_prefixes)

            self.assertEqual(len(v4_prefixes), 1)
            self.assertTrue(blocked)
            self.assertEqual(str(prefix), "87.240.128.0/18")


if __name__ == "__main__":
    unittest.main()
