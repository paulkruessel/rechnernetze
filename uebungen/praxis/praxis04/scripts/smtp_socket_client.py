#!/usr/bin/env python3
import argparse
import base64
import getpass
import socket
import ssl
import time

SMTP_HOST = "asmtp.htwg-konstanz.de"
SMTP_PORT = 587

def recv_print(sock, label="S"):
    data = sock.recv(4096)
    print(f"[{label}] {data.decode('utf-8', errors='replace').rstrip()}")
    return data

def send_line(sock, line: str, secret: bool = False):
    shown = "***" if secret else line
    print(f"[C] {shown}")
    sock.sendall((line + "\r\n").encode("utf-8"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True, help="HTWG/RZ username")
    parser.add_argument("--from-envelope", required=True, help="SMTP MAIL FROM address")
    parser.add_argument("--from-header", required=True, help="From header shown in email")
    parser.add_argument("--to", required=True, help="Recipient address")
    parser.add_argument("--subject", default="RN Labor SMTP Socket Test")
    parser.add_argument("--body", default="Dies ist eine Testmail aus dem RN-Labor per Python-Socket.")
    parser.add_argument("--host", default=SMTP_HOST)
    parser.add_argument("--port", type=int, default=SMTP_PORT)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    password = getpass.getpass("HTWG/RZ password: ")

    plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    plain.settimeout(args.timeout)
    print(f"[INFO] connect {(args.host, args.port)}")
    plain.connect((args.host, args.port))
    recv_print(plain)

    send_line(plain, "ehlo localhost")
    recv_print(plain)

    send_line(plain, "starttls")
    recv_print(plain)
    time.sleep(1)

    context = ssl.create_default_context()
    sock = context.wrap_socket(plain, server_hostname=args.host)
    print("[INFO] TLS established")

    send_line(sock, "ehlo localhost")
    recv_print(sock)

    send_line(sock, "auth login")
    recv_print(sock)

    user_b64 = base64.b64encode(args.username.encode("utf-8")).decode("utf-8")
    pw_b64 = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    send_line(sock, user_b64, secret=True)
    recv_print(sock)
    send_line(sock, pw_b64, secret=True)
    recv_print(sock)

    send_line(sock, f"mail from:<{args.from_envelope}>")
    recv_print(sock)
    send_line(sock, f"rcpt to:<{args.to}>")
    recv_print(sock)
    send_line(sock, "data")
    recv_print(sock)

    msg = (
        f"from: {args.from_header}\r\n"
        f"to: {args.to}\r\n"
        f"subject: {args.subject}\r\n"
        "\r\n"
        f"{args.body}\r\n"
        "."
    )
    send_line(sock, msg)
    recv_print(sock)

    send_line(sock, "quit")
    recv_print(sock)
    sock.close()
    print("[INFO] done")

if __name__ == "__main__":
    main()
