#!/usr/bin/env python3
import argparse
import socket
import struct

def create_request(task_id: int, operation: str, numbers: list[int]) -> bytes:
    if len(operation) != 3:
        raise ValueError("Operation must be one of SUM, PRO, MIN, MAX")
    message = struct.pack("!I", task_id)
    message += operation.encode("utf-8")
    message += struct.pack("!B", len(numbers))
    for z in numbers:
        message += struct.pack("!i", z)
    return message

def parse_response(message: bytes):
    task_id, result = struct.unpack("!Ii", message[:8])
    return task_id, result

def run_tcp(args, request: bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(args.timeout)
    print(f"[CLIENT TCP] before bind/connect getsockname={sock.getsockname()}")
    if args.bind_ip or args.bind_port is not None:
        bind_addr = (args.bind_ip or "", args.bind_port or 0)
        sock.bind(bind_addr)
        print(f"[CLIENT TCP] after explicit bind getsockname={sock.getsockname()}")
    print(f"[CLIENT TCP] connecting to {(args.server_ip, args.server_port)}")
    sock.connect((args.server_ip, args.server_port))
    print(f"[CLIENT TCP] after connect local getsockname={sock.getsockname()} peer={sock.getpeername()}")
    print(f"[CLIENT TCP] TX {len(request)} bytes: {request.hex()}")
    sock.sendall(request)
    response = sock.recv(1024)
    print(f"[CLIENT TCP] RX {len(response)} bytes: {response.hex()}")
    print(f"[CLIENT TCP] parsed response={parse_response(response)}")
    sock.close()

def run_udp(args, request: bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    print(f"[CLIENT UDP] before bind/send getsockname={sock.getsockname()}")
    if args.bind_ip or args.bind_port is not None:
        bind_addr = (args.bind_ip or "", args.bind_port or 0)
        sock.bind(bind_addr)
        print(f"[CLIENT UDP] after explicit bind getsockname={sock.getsockname()}")
    print(f"[CLIENT UDP] TX to {(args.server_ip, args.server_port)} {len(request)} bytes: {request.hex()}")
    sock.sendto(request, (args.server_ip, args.server_port))
    print(f"[CLIENT UDP] after send local getsockname={sock.getsockname()}")
    response, addr = sock.recvfrom(1024)
    print(f"[CLIENT UDP] RX from {addr} {len(response)} bytes: {response.hex()}")
    print(f"[CLIENT UDP] parsed response={parse_response(response)}")
    sock.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", choices=["tcp", "udp"], default="tcp")
    parser.add_argument("--server-ip", default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=50001)
    parser.add_argument("--bind-ip", default=None, help="Optional local source IP; for hotspot use your own WLAN IP")
    parser.add_argument("--bind-port", type=int, default=None, help="Optional local source port")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--task-id", type=int, default=5000)
    parser.add_argument("--op", choices=["SUM", "PRO", "MIN", "MAX"], default="SUM")
    parser.add_argument("--numbers", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    args = parser.parse_args()

    socket.setdefaulttimeout(args.timeout)
    print(f"[CLIENT] socket.setdefaulttimeout={args.timeout}")
    print(f"[CLIENT] test={args.op}({args.numbers}) task_id={args.task_id}")
    request = create_request(args.task_id, args.op, args.numbers)
    if args.proto == "tcp":
        run_tcp(args, request)
    else:
        run_udp(args, request)

if __name__ == "__main__":
    main()
