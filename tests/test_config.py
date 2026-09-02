import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "src" / "ssh_sftp.py"
SPEC = importlib.util.spec_from_file_location("ssh_sftp", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ConfigTests(unittest.TestCase):
    def test_load_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "hosts.json"
            config.write_text(
                json.dumps(
                    {
                        "hosts": [
                            {
                                "name": "test-host",
                                "hostname": "192.0.2.25",
                                "username": "tester",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            hosts = MODULE.load_hosts(config)

            self.assertEqual(len(hosts), 1)
            self.assertEqual(hosts[0].port, 22)
            self.assertEqual(hosts[0].hostname, "192.0.2.25")

    def test_empty_config_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "hosts.json"
            config.write_text('{"hosts": []}', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "at least one host"):
                MODULE.load_hosts(config)


if __name__ == "__main__":
    unittest.main()
