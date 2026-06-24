import unittest

from vc_guardian import get_state_defaults, build_emergency_ping


class ConfigTests(unittest.TestCase):
    def test_state_defaults_include_admin_config_keys(self):
        defaults = get_state_defaults()
        self.assertIn("voice_channel_id", defaults)
        self.assertIn("text_channel_id", defaults)
        self.assertIn("emergency_ping", defaults)

    def test_build_emergency_ping_uses_member_mention(self):
        self.assertEqual(build_emergency_ping(123456789), "<@123456789>")

    def test_build_emergency_ping_returns_empty_when_unset(self):
        self.assertEqual(build_emergency_ping(None), "")


if __name__ == "__main__":
    unittest.main()
