import unittest

from generate_nft_blacklist import make_nft_config


class GenerateNftBlacklistTests(unittest.TestCase):
    def test_general_profile_generates_plain_sets_only(self):
        config = make_nft_config(["10.0.0.0/24"], [], usage_profile="vm_input")

        self.assertIn("set blacklist_v4", config)
        self.assertNotIn("chain input", config)
        self.assertIn("ip saddr @blacklist_v4", config)

    def test_vk_profile_uses_vk_set_names_and_forward_example(self):
        config = make_nft_config(["10.0.0.0/24"], ["2001:db8::/32"], usage_profile="vk_forward")

        self.assertIn("set blacklist_vk_v4", config)
        self.assertIn("set blacklist_vk_v6", config)
        self.assertNotIn("chain forward", config)
        self.assertIn("ip daddr @blacklist_vk_v4", config)
        self.assertIn("ip6 daddr @blacklist_vk_v6", config)


if __name__ == "__main__":
    unittest.main()
