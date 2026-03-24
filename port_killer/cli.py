import argparse
import signal
import sys

import psutil


def find_process_by_port(port: int) -> list[psutil.Process]:
    """Return all processes listening on the given port."""
    matches = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "status"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status in (
                    psutil.CONN_LISTEN,
                    psutil.CONN_ESTABLISHED,
                    "LISTEN",
                    "ESTABLISHED",
                ):
                    matches.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return matches


def describe_process(proc: psutil.Process) -> str:
    """Build a human-readable one-liner for a process."""
    try:
        name = proc.name()
        pid = proc.pid
        cmdline = proc.cmdline()
        cmd = " ".join(cmdline) if cmdline else name
        # Truncate long command lines
        if len(cmd) > 80:
            cmd = cmd[:77] + "..."
        return f"  PID {pid}  {name}  —  {cmd}"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return f"  PID {proc.pid}  (details unavailable)"


def kill_process(proc: psutil.Process) -> None:
    try:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
    except psutil.NoSuchProcess:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="port-kill",
        description="Kill the process listening on a port.",
    )
    parser.add_argument("port", type=int, help="Port number to free")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    port: int = args.port
    force: bool = args.force

    if port < 1 or port > 65535:
        print(f"Error: {port} is not a valid port number (1-65535).", file=sys.stderr)
        sys.exit(1)

    processes = find_process_by_port(port)

    if not processes:
        print(f"No process found on port {port}.")
        sys.exit(0)

    print(f"Port {port} is used by:")
    for proc in processes:
        print(describe_process(proc))

    if not force:
        try:
            answer = input("\nKill? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)
        if answer not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    for proc in processes:
        pid = proc.pid
        kill_process(proc)
        print(f"Killed PID {pid}.")
