import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pylib.whois import WhoisError

SCRIPT = str(Path(__file__).resolve().parent.parent / "get_description.py")
UNNAMED = (
    "AS64496 -no-description-\n"
    "AS64497 -no-description-\n"
    "AS64498 -no-description-\n"
)


class GetDescriptionTests(unittest.TestCase):
    def run_script(self, whois):
        with tempfile.TemporaryDirectory() as tmpdir:
            names = Path(tmpdir) / "all-ru-asn.txt"
            names.write_text(UNNAMED, encoding="utf-8")
            with mock.patch("pylib.whois.whois_query", whois), \
                    mock.patch.object(sys, "argv", ["get_description.py", str(names)]), \
                    mock.patch("sys.stdout"):
                try:
                    runpy.run_path(SCRIPT, run_name="__main__")
                    exit_message = None
                except SystemExit as exc:
                    exit_message = exc.code
            return names.read_text(encoding="utf-8"), exit_message

    def test_names_are_written_back(self):
        whois = mock.Mock(side_effect=["ONE-AS (One LLC)", "TWO-AS (Two LLC)", "THREE-AS (Three LLC)"])
        content, exit_message = self.run_script(whois)
        self.assertIsNone(exit_message)
        self.assertEqual(content.splitlines()[1], "AS64497 TWO-AS (Two LLC)")

    def test_refusal_stops_the_run_and_leaves_the_file_unchanged(self):
        whois = mock.Mock(side_effect=["ONE-AS (One LLC)", WhoisError("refused: %ERROR:201: access denied")])
        content, exit_message = self.run_script(whois)
        self.assertEqual(content, UNNAMED)
        self.assertIn("%ERROR:201", exit_message)
        self.assertEqual(whois.call_count, 2)


if __name__ == "__main__":
    unittest.main()
