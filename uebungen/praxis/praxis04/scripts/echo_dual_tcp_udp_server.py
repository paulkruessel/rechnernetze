#!/usr/bin/env python3
import argparse
import socket
import time
from threading import Thread

RUNNING = True

def tcp_loop(tcp_sock):
    global RUNNING
    print(f"[TCP ECHO] Listening on {tcp_sock.getsockname()}")
    while RUNNING:
        try:
            conn, addr = tcp_sock.accept()
            print(f"[TCP ECHO] accepted {addr}")
            Thread(target=tcp_receive, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
        except OSError:
            break

def tcp_receive(conn, addr):
    try:
        while True:
            data = conn.recv(1024)
            if data == b"":
                break
            print(f"[TCP ECHO] RX from {addr}: {data!r}")
            conn.sendall(data)
    except socket.timeout:
        print(f"[TCP ECHO] timeout {addr}")
    finally:
        conn.close()
        print(f"[TCP ECHO] closed {addr}")

def udp_loop(udp_sock):
    global RUNNING
    print(f"[UDP ECHO] Listening on {udp_sock.getsockname()}")
    while RUNNING:
        try:
            data, addr = udp_sock.recvfrom(1024)
            print(f"[UDP ECHO] RX from {addr}: {data!r}")
            udp_sock.sendto(data, addr)
        except socket.timeout:
            continue
        except OSError:
            break

def main():
    global RUNNING
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.settimeout(args.timeout)
    tcp_sock.bind((args.ip, args.port))
    tcp_sock.listen(5)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(args.timeout)
    udp_sock.bind((args.ip, args.port))

    Thread(target=tcp_loop, args=(tcp_sock,), daemon=True).start()
    Thread(target=udp_loop, args=(udp_sock,), daemon=True).start()

    print(f"[DUAL ECHO] TCP and UDP are bound to the same numeric port {args.port}")
    end = time.time() + args.seconds
    try:
        while time.time() < end:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    RUNNING = False
    tcp_sock.close()
    udp_sock.close()
    print("[DUAL ECHO] Stopped")

if __name__ == "__main__":
    main()
