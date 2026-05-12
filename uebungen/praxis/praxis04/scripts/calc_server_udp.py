#!/usr/bin/env python3
import argparse
import socket
import struct
import time

def parse_request(message: bytes):
    offset = 0
    task_id = struct.unpack("!I", message[offset:offset+4])[0]
    offset += 4
    operation = message[offset:offset+3].decode("utf-8")
    offset += 3
    n = struct.unpack("!B", message[offset:offset+1])[0]
    offset += 1
    numbers = []
    for _ in range(n):
        numbers.append(struct.unpack("!i", message[offset:offset+4])[0])
        offset += 4
    return task_id, operation, numbers

def create_response(task_id: int, result: int) -> bytes:
    return struct.pack("!Ii", task_id, result)

def calculate(operation: str, numbers: list[int]) -> int:
    if operation == "SUM":
        return sum(numbers)
    if operation == "PRO":
        result = 1
        for x in numbers:
            result *= x
        return result
    if operation == "MIN":
        return min(numbers)
    if operation == "MAX":
        return max(numbers)
    raise ValueError(f"Unknown operation: {operation}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50002)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    sock.bind((args.ip, args.port))
    end = time.time() + args.seconds
    print(f"[UDP SERVER] Listening on {sock.getsockname()} for {args.seconds}s")
    while time.time() < end:
        try:
            data, addr = sock.recvfrom(2048)
            print(f"[UDP SERVER] RX from {addr}: {data.hex()}")
            task_id, operation, numbers = parse_request(data)
            result = calculate(operation, numbers)
            response = create_response(task_id, result)
            print(f"[UDP SERVER] Parsed: id={task_id}, op={operation}, numbers={numbers}, result={result}")
            print(f"[UDP SERVER] TX to {addr}: {response.hex()}")
            sock.sendto(response, addr)
        except socket.timeout:
            print("[UDP SERVER] Timeout waiting")
        except Exception as exc:
            print(f"[UDP SERVER] Error: {type(exc).__name__}: {exc}")
    sock.close()
    print("[UDP SERVER] Stopped")

if __name__ == "__main__":
    main()
