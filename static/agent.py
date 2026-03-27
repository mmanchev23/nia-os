import sys
import time
import json
import signal
import urllib.error
import urllib.request


DEFAULT_INTERVAL = 15


def get_config() -> tuple[str, str, int]:
    if len(sys.argv) < 3:
        print("Usage: python3 agent.py <SERVER_URL> <AGENT_KEY> [INTERVAL]")
        print("Error: Missing required arguments.")
        sys.exit(1)

    server_url = sys.argv[1]
    agent_key = sys.argv[2]
    interval = DEFAULT_INTERVAL

    if len(sys.argv) >= 4:
        try:
            parsed_interval = int(sys.argv[3])

            if parsed_interval > 0:
                interval = parsed_interval
            else:
                print(
                    f"Warning: Interval must be > 0. Using default ({DEFAULT_INTERVAL}s)."
                )
        except ValueError:
            print(
                f"Warning: Invalid interval format. Using default ({DEFAULT_INTERVAL}s)."
            )

    if not server_url.startswith("http"):
        print("Error: SERVER_URL must start with http:// or https://")
        sys.exit(1)

    return server_url, agent_key, interval


def get_cpu_usage() -> tuple[float, float]:
    try:
        with open("/proc/stat", "r") as f:
            line = f.readline()

        fields = [float(x) for x in line.split()[1:]]
        idle = fields[3]
        total = sum(fields)
        return idle, total
    except FileNotFoundError:
        return 0, 0


def get_ram_usage() -> float:
    try:
        mem = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mem[parts[0].rstrip(":")] = int(parts[1])

        if "MemTotal" in mem and "MemAvailable" in mem:
            total = mem["MemTotal"]
            available = mem["MemAvailable"]
            used = total - available
            return (used / total) * 100.0

        return 0.0
    except FileNotFoundError:
        return 0.0


def get_disk_usage(path: str = "/") -> float:
    import os

    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free
        return (used / total) * 100.0
    except Exception:
        return 0.0


def send_metrics(
    server_url: str, agent_key: str, cpu: float, ram: float, disk: float
) -> None:
    payload = {
        "agent_key": agent_key,
        "cpu_percent": round(cpu, 2),
        "ram_percent": round(ram, 2),
        "disk_percent": round(disk, 2),
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        server_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "NIA-OS-Agent/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"Error {response.status}: Server rejected payload")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP Error {e.code}: {e.reason} -> {error_body}")
    except urllib.error.URLError as e:
        print(f"Connection Failed: {e.reason}")
    except Exception as e:
        print(f"Transmission Error: {e}")


def main() -> None:
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    SERVER_URL, AGENT_KEY, INTERVAL = get_config()

    print("NIA-OS Agent Started")
    print(f"Target:   {SERVER_URL}")
    print(f"Node ID:  {AGENT_KEY}")
    print(f"Interval: {INTERVAL} seconds")
    print("--------------------------------")

    prev_idle, prev_total = get_cpu_usage()
    time.sleep(1)

    while True:
        try:
            curr_idle, curr_total = get_cpu_usage()
            idle_delta = curr_idle - prev_idle
            total_delta = curr_total - prev_total

            cpu_percent = 0.0

            if total_delta > 0:
                cpu_percent = 100.0 * (1.0 - idle_delta / total_delta)

            prev_idle, prev_total = curr_idle, curr_total

            ram_percent = get_ram_usage()
            disk_percent = get_disk_usage()

            send_metrics(SERVER_URL, AGENT_KEY, cpu_percent, ram_percent, disk_percent)
            time.sleep(INTERVAL)
        except Exception as e:
            print(f"Runtime Error: {e}")
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
