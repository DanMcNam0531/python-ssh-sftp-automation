# Python SSH/SFTP Automation

## Overview

This Python project automates authorized SFTP uploads across multiple lab hosts while handling unreachable systems, timeouts, authentication failures, and transfer errors without exposing credentials.

## Features

- JSON-based multi-host configuration
- Configurable SSH port and connection timeout
- Strict known-host verification through Paramiko
- Password collection through an environment variable or secure prompt
- Per-host success and error reporting
- Continued processing when an individual host is offline
- Nonzero exit status when one or more transfers fail

## Project Structure

```text
├── hosts.example.json
├── requirements.txt
├── src/
│   └── ssh_sftp.py
└── tests/
    └── test_config.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage

```bash
export SFTP_PASSWORD='use-a-secret-manager-in-production'
python src/ssh_sftp.py \
  --config hosts.json \
  --local-file example.txt \
  --remote-path /tmp/example.txt \
  --timeout 3
```

Copy `hosts.example.json` to `hosts.json` and replace the documentation-range addresses with authorized lab systems. The Python `.gitignore` prevents local environment and common secret files from being committed.

## Validation

- Python source passes compilation checks.
- Unit tests validate host configuration and reject empty inventories.
- Example addresses use the RFC 5737 documentation range.
- Passwords and private host information are excluded from the repository.

## Run Tests

```bash
python -m unittest tests/test_config.py -v
```

## Authorized Use

Use this tool only with systems you own or are explicitly authorized to administer.

## Author

Daniel McNamara  
B.S. Cybersecurity Candidate, Lewis University — December 2026
