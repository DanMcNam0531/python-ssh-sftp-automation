#!/usr/bin/env python3
"""Authorized multi-host SFTP uploader with strict host-key checking."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Host:
    name: str
    hostname: str
    port: int
    username: str


def load_hosts(config_path: Path) -> list[Host]:
    """Load and validate host definitions from a JSON configuration file."""
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    hosts: list[Host] = []

    for item in raw.get("hosts", []):
        hosts.append(
            Host(
                name=str(item["name"]),
                hostname=str(item["hostname"]),
                port=int(item.get("port", 22)),
                username=str(item["username"]),
            )
        )

    if not hosts:
        raise ValueError("Configuration must contain at least one host")

    return hosts


def upload_file(
    host: Host,
    local_path: Path,
    remote_path: str,
    password: str,
    timeout: float,
) -> tuple[bool, str]:
    """Upload one file and return a success flag with a status message."""
    import paramiko

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(
            hostname=host.hostname,
            port=host.port,
            username=host.username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout,
        )
        with client.open_sftp() as sftp:
            sftp.put(str(local_path), remote_path)
        return True, f"{host.name}: upload completed"
    except (paramiko.SSHException, socket.timeout, OSError) as exc:
        return False, f"{host.name}: upload failed ({type(exc).__name__})"
    finally:
        client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a file to authorized SSH/SFTP hosts")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--local-file", type=Path, required=True)
    parser.add_argument("--remote-path", required=True)
    parser.add_argument("--timeout", type=float, default=3.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.local_file.is_file():
        raise SystemExit(f"Local file not found: {args.local_file}")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero")

    hosts = load_hosts(args.config)
    password = os.environ.get("SFTP_PASSWORD") or getpass.getpass("SFTP password: ")
    failures = 0

    for host in hosts:
        success, message = upload_file(
            host=host,
            local_path=args.local_file,
            remote_path=args.remote_path,
            password=password,
            timeout=args.timeout,
        )
        print(message)
        failures += int(not success)

    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
