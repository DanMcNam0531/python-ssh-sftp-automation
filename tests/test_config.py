import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


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

    def test_custom_port_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "hosts.json"
            config.write_text(
                '{"hosts":[{"name":"lab","hostname":"192.0.2.30",'
                '"port":2222,"username":"analyst"}]}',
                encoding="utf-8",
            )

            host = MODULE.load_hosts(config)[0]

            self.assertEqual(host.port, 2222)
            self.assertEqual(host.username, "analyst")

    def test_upload_success_message(self) -> None:
        class FakeSFTP:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def put(self, local_path, remote_path):
                self.transfer = (local_path, remote_path)

        class FakeClient:
            def load_system_host_keys(self):
                pass

            def set_missing_host_key_policy(self, policy):
                self.policy = policy

            def connect(self, **kwargs):
                self.connection = kwargs

            def open_sftp(self):
                return FakeSFTP()

            def close(self):
                pass

        fake_paramiko = SimpleNamespace(
            SSHClient=FakeClient,
            RejectPolicy=lambda: object(),
            SSHException=RuntimeError,
        )
        host = MODULE.Host("linux-lab-01", "192.0.2.25", 22, "analyst")

        with patch.dict(sys.modules, {"paramiko": fake_paramiko}):
            success, message = MODULE.upload_file(
                host, Path("sample.txt"), "/tmp/sample.txt", "test-only", 3
            )

        self.assertTrue(success)
        self.assertEqual(message, "linux-lab-01: upload completed")

    def test_timeout_is_reported_without_sensitive_details(self) -> None:
        class TimeoutClient:
            def load_system_host_keys(self):
                pass

            def set_missing_host_key_policy(self, policy):
                pass

            def connect(self, **kwargs):
                raise TimeoutError("private connection detail")

            def close(self):
                pass

        fake_paramiko = SimpleNamespace(
            SSHClient=TimeoutClient,
            RejectPolicy=lambda: object(),
            SSHException=RuntimeError,
        )
        host = MODULE.Host("offline-lab-host", "192.0.2.99", 22, "analyst")

        with patch.dict(sys.modules, {"paramiko": fake_paramiko}):
            success, message = MODULE.upload_file(
                host, Path("sample.txt"), "/tmp/sample.txt", "test-only", 1
            )

        self.assertFalse(success)
        self.assertEqual(message, "offline-lab-host: upload failed (TimeoutError)")
        self.assertNotIn("private connection detail", message)


if __name__ == "__main__":
    unittest.main()
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
