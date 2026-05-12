#!/usr/bin/env python3
import argparse
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_tcp(host: str, port: int, timeout: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        err = sock.connect_ex((host, port))
        if err == 0:
            try:
                sock.sendall(b"RN-LAB-ECHO-TEST\r\n")
                try:
                    data = sock.recv(1024)
                except socket.timeout:
                    data = b""
            finally:
                sock.close()
            return port, "open", "connect_ex=0", data
        return port, "closed_or_filtered", f"connect_ex={err}", b""
    except Exception as exc:
        return port, "error", f"{type(exc).__name__}: {exc}", b""
    finally:
        try:
            sock.close()
        except Exception:
            pass

def scan_udp(host: str, port: int, timeout: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    payload = b"RN-LAB-ECHO-TEST"
    try:
        sock.sendto(payload, (host, port))
        try:
            data, addr = sock.recvfrom(1024)
            return port, "response_open_or_echo", f"from={addr}", data
        except ConnectionResetError as exc:
            # Windows often shows closed UDP as WinError 10054.
            return port, "closed_icmp_port_unreachable", f"{type(exc).__name__}: {exc}", b""
        except OSError as exc:
            # Linux may expose ICMP errors differently depending on platform.
            return port, "os_error_probably_closed", f"{type(exc).__name__}: {exc}", b""
        except socket.timeout:
            return port, "no_response_open_or_filtered", "timeout", b""
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", choices=["tcp", "udp"], required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=50)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--workers", type=int, default=50)
    args = parser.parse_args()

    fn = scan_tcp if args.proto == "tcp" else scan_udp
    print(f"[SCAN] proto={args.proto} host={args.host} ports={args.start}-{args.end} timeout={args.timeout}s workers={args.workers}")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fn, args.host, port, args.timeout) for port in range(args.start, args.end + 1)]
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda x: x[0])
    print("port;status;detail;payload_hex;payload_text")
    for port, status, detail, data in results:
        text = data.decode("utf-8", errors="replace").replace("\n", "\\n").replace("\r", "\\r")
        print(f"{port};{status};{detail};{data.hex()};{text}")

    interesting = [r for r in results if r[1] in ("open", "response_open_or_echo", "closed_icmp_port_unreachable")]
    print("[SUMMARY]")
    for r in interesting:
        print(f"{args.proto.upper()} port {r[0]}: {r[1]} {r[2]} payload={r[3]!r}")

if __name__ == "__main__":
    main()
