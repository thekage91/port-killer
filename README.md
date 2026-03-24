# port-killer

A dead simple CLI to free occupied ports. It shows you exactly what process is holding a port, asks for confirmation, and kills it.

## Features

- Identifies the process (PID, name, and full command) using a port
- Confirmation prompt before killing — no accidental kills
- `--force` flag to skip the prompt for scripting and automation
- Handles multiple processes on the same port
- Graceful shutdown: sends `SIGTERM` first, escalates to `SIGKILL` after 3 s
- Cross-platform via [psutil](https://github.com/giampaolo/psutil) (macOS, Linux, Windows)

## Installation

Requires Python 3.9+.

```bash
pip install port-killer
```

Or install from source:

```bash
git clone https://github.com/thekage91/port-killer.git
cd port-killer
pip install -e .
```

## Usage

```bash
port-killer <port> [--force]
```

### Examples

Kill the process on port 3000 (with confirmation):

```
$ port-killer 3000
Port 3000 is used by:
  PID 12345  node  —  node server.js

Kill? [y/N] y
Killed PID 12345.
```

Kill immediately without prompt:

```bash
port-killer 8080 --force
```

Nothing is running on the port:

```
$ port-killer 9999
No process found on port 9999.
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | `-f` | Skip the confirmation prompt |
| `--help` | `-h` | Show help message and exit |

## How it works

1. Iterates over all running processes and their network connections using `psutil`.
2. Matches connections whose local port equals the requested port and whose status is `LISTEN` or `ESTABLISHED`.
3. Prints the process name and command line so you know what you're about to kill.
4. Asks `Kill? [y/N]` (skipped with `--force`).
5. Sends `SIGTERM`; if the process doesn't exit within 3 seconds, sends `SIGKILL`.

## License

MIT
