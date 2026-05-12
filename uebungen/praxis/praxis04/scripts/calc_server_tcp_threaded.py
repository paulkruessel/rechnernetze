#!/usr/bin/env python3
import argparse
import socket
import struct
from threading import Thread

RUNNING = True

def parse_request(message: bytes):
    if len(message) < 8:
        raise ValueError(f"Request too short: {len(message)} bytes")
    offset = 0
    task_id = struct.unpack("!I", message[offset:offset+4])[0]
    offset += 4
    operation = message[offset:offset+3].decode("utf-8")
    offset += 3
    n = struct.unpack("!B", message[offset:offset+1])[0]
    offset += 1
    expected_len = 4 + 3 + 1 + 4 * n
    if len(message) < expected_len:
        raise ValueError(f"Request incomplete: got {len(message)} bytes, expected {expected_len}")
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

def receive(conn: socket.socket, addr):
    print(f"[TCP SERVER] Client connected: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if data == b"":
                print(f"[TCP SERVER] Client closed connection: {addr}")
                break
            print(f"[TCP SERVER] RX from {addr}: {data.hex()}")
            task_id, operation, numbers = parse_request(data)
            result = calculate(operation, numbers)
            response = create_response(task_id, result)
            print(f"[TCP SERVER] Parsed: id={task_id}, op={operation}, numbers={numbers}, result={result}")
            print(f"[TCP SERVER] TX to {addr}: {response.hex()}")
            conn.sendall(response)
    except socket.timeout:
        print(f"[TCP SERVER] Timeout for {addr}")
    except Exception as exc:
        print(f"[TCP SERVER] Error for {addr}: {type(exc).__name__}: {exc}")
    finally:
        conn.close()
        print(f"[TCP SERVER] Connection closed: {addr}")

def listen(sock: socket.socket):
    global RUNNING
    while RUNNING:
        try:
            conn, addr = sock.accept()
            Thread(target=receive, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            RUNNING = False
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="Server bind IP, e.g. 127.0.0.1 or hotspot/WLAN IP")
    parser.add_argument("--port", type=int, default=50001)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    socket.setdefaulttimeout(args.timeout)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.ip, args.port))
    sock.listen(5)
    print(f"[TCP SERVER] Listening on {sock.getsockname()} timeout={args.timeout}s")
    try:
        listen(sock)
    finally:
        sock.close()
        print("[TCP SERVER] Stopped")

if __name__ == "__main__":
    main()
