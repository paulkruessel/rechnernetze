#!/usr/bin/env python3
import argparse
import socket

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", choices=["tcp", "udp"], required=True)
    parser.add_argument("--server-ip", default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=50000)
    parser.add_argument("--message", default="Hello, World!")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    data = args.message.encode("utf-8")
    if args.proto == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(args.timeout)
        print(f"[TCP CLIENT] before connect local={sock.getsockname()}")
        sock.connect((args.server_ip, args.server_port))
        print(f"[TCP CLIENT] after connect local={sock.getsockname()} peer={sock.getpeername()}")
        print(f"[TCP CLIENT] TX: {data!r}")
        sock.sendall(data)
        rx = sock.recv(1024)
        print(f"[TCP CLIENT] RX: {rx!r}")
        sock.close()
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(args.timeout)
        print(f"[UDP CLIENT] before send local={sock.getsockname()}")
        print(f"[UDP CLIENT] TX: {data!r}")
        sock.sendto(data, (args.server_ip, args.server_port))
        print(f"[UDP CLIENT] after send local={sock.getsockname()}")
        rx, addr = sock.recvfrom(1024)
        print(f"[UDP CLIENT] RX from {addr}: {rx!r}")
        sock.close()

if __name__ == "__main__":
    main()
