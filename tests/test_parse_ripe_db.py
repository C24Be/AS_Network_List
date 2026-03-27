import json
import tempfile
import unittest
from pathlib import Path

from parse_ripe_db import parse


class ParseRipeDbTests(unittest.TestCase):
    def test_skips_non_ru_last_record_and_normalizes_last_ru_record(self):
        sample = """\
inetnum: 10.0.0.0 - 10.0.0.255
netname: TEST1
country: RU
org: ORG-1
descr: desc1
inetnum: 20.0.0.0 - 20.0.0.255
netname: TEST2
country: US
org: ORG-2
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "ripe.db.inetnum"
            output_text = Path(tmpdir) / "out.txt"
            output_json = Path(tmpdir) / "out.json"
            source.write_text(sample, encoding="latin-1")

            parse(str(source), str(output_text), str(output_json))

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["inetnum"], ["10.0.0.0/24"])
            self.assertEqual(payload[0]["country"], "RU")

            text_lines = output_text.read_text(encoding="utf-8").splitlines()
            self.assertEqual(text_lines, ["10.0.0.0/24 TEST1 (ORG-1) [desc1]"])


if __name__ == "__main__":
    unittest.main()
