#!/usr/bin/env python3
import json
import random
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path


HOST = "127.0.0.1"
BASE_TIMEOUT = 2.0


def message2bytes(payload: dict) -> bytes:
	raw = json.dumps(payload).encode("utf-8")
	return struct.pack("!I", len(raw)) + raw


def recv_exact(conn: socket.socket, n: int) -> bytes:
	data = b""
	while len(data) < n:
		chunk = conn.recv(n - len(data))
		if not chunk:
			raise ConnectionError("socket closed")
		data += chunk
	return data


def recv_message(conn: socket.socket, timeout: float = BASE_TIMEOUT) -> dict:
	conn.settimeout(timeout)
	header = recv_exact(conn, 4)
	(size,) = struct.unpack("!I", header)
	payload = recv_exact(conn, size)
	return json.loads(payload.decode("utf-8"))


def send_message(conn: socket.socket, payload: dict):
	conn.sendall(message2bytes(payload))


def send_raw_payload(conn: socket.socket, raw_payload: bytes):
	conn.sendall(struct.pack("!I", len(raw_payload)) + raw_payload)


def connect_client(port: int) -> socket.socket:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(BASE_TIMEOUT)
	sock.connect((HOST, port))
	return sock


def collect_types(conn: socket.socket, needed_types: set[str], timeout: float = BASE_TIMEOUT) -> list[dict]:
	deadline = time.time() + timeout
	collected: list[dict] = []
	found = set()
	while time.time() < deadline and found != needed_types:
		try:
			msg = recv_message(conn, timeout=max(0.1, deadline - time.time()))
		except (socket.timeout, TimeoutError):
			continue
		collected.append(msg)
		msg_type = msg.get("type", "")
		if msg_type in needed_types:
			found.add(msg_type)
	return collected


def register_client(conn: socket.socket, nick: str, udp_port: int):
	send_message(conn, {"type": "REGISTER", "nick": nick, "udp": udp_port})
	msgs = collect_types(conn, {"REGISTER_OK", "USER_LIST"}, timeout=3.0)
	types = {m.get("type", "") for m in msgs}
	if "REGISTER_OK" not in types or "USER_LIST" not in types:
		raise AssertionError(f"REGISTER did not complete successfully, got: {types}")


def drain_socket(conn: socket.socket, max_wait: float = 0.3):
	deadline = time.time() + max_wait
	while time.time() < deadline:
		try:
			recv_message(conn, timeout=0.1)
		except (socket.timeout, TimeoutError, ConnectionError, json.JSONDecodeError):
			break


def wait_for_server(port: int, timeout: float = 5.0):
	deadline = time.time() + timeout
	while time.time() < deadline:
		try:
			with socket.create_connection((HOST, port), timeout=0.2):
				return
		except OSError:
			time.sleep(0.05)
	raise RuntimeError("Server did not start in time")


def run_status_test(name: str, fn):
	sys.stdout.write(f"Testing {name}...")
	sys.stdout.flush()
	try:
		fn()
		sys.stdout.write(" ok!\n")
		return True
	except Exception as exc:
		sys.stdout.write(" failed!\n")
		print(f"  reason: {exc}")
		return False


def main():
	here = Path(__file__).resolve().parent
	server_path = here / "chat_server.py"
	port = random.randint(52000, 59000)

	server_proc = subprocess.Popen(
		[
			sys.executable,
			str(server_path),
			"--ip",
			HOST,
			"--port",
			str(port),
			"--timeout",
			"1",
		],
		cwd=str(here),
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)

	try:
		wait_for_server(port)

		def test_register_success():
			conn = connect_client(port)
			try:
				register_client(conn, "alice", 40001)
			finally:
				conn.close()

		def test_register_fail_empty_nick():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "REGISTER", "nick": "", "udp": 40002})
				msg = recv_message(conn)
				if msg.get("type") != "REGISTER_FAIL":
					raise AssertionError(f"Expected REGISTER_FAIL, got {msg}")
			finally:
				conn.close()

		def test_register_fail_missing_udp():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "REGISTER", "nick": "bob"})
				msg = recv_message(conn)
				if msg.get("type") != "REGISTER_FAIL":
					raise AssertionError(f"Expected REGISTER_FAIL, got {msg}")
			finally:
				conn.close()

		def test_broadcast_without_register():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "BROADCAST", "msg": "hello"})
				msg = recv_message(conn)
				if msg.get("type") != "MESSAGE_FAIL":
					raise AssertionError(f"Expected MESSAGE_FAIL, got {msg}")
			finally:
				conn.close()

		def test_broadcast_empty_text():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "BROADCAST", "msg": ""})
				msg = recv_message(conn)
				if msg.get("type") != "MESSAGE_FAIL":
					raise AssertionError(f"Expected MESSAGE_FAIL, got {msg}")
			finally:
				conn.close()

		def test_message_type_fail():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "MESSAGE", "msg": "peer-text"})
				msg = recv_message(conn)
				if msg.get("type") != "MESSAGE_FAIL":
					raise AssertionError(f"Expected MESSAGE_FAIL, got {msg}")
			finally:
				conn.close()

		def test_unknown_type_fail():
			conn = connect_client(port)
			try:
				send_message(conn, {"type": "WHATEVER", "msg": "x"})
				msg = recv_message(conn)
				if msg.get("type") != "MESSAGE_FAIL":
					raise AssertionError(f"Expected MESSAGE_FAIL, got {msg}")
			finally:
				conn.close()

		def test_invalid_json_fail():
			conn = connect_client(port)
			try:
				send_raw_payload(conn, b"{")
				msg = recv_message(conn)
				if msg.get("type") != "MESSAGE_FAIL":
					raise AssertionError(f"Expected MESSAGE_FAIL, got {msg}")
			finally:
				conn.close()

		def test_broadcast_success_after_register():
			conn_a = connect_client(port)
			conn_b = connect_client(port)
			try:
				register_client(conn_a, "charlie", 40011)
				register_client(conn_b, "dana", 40012)
				drain_socket(conn_a)
				drain_socket(conn_b)

				text = "hello-everyone"
				send_message(conn_a, {"type": "BROADCAST", "msg": text})

				msg_a = recv_message(conn_a, timeout=3.0)
				msg_b = recv_message(conn_b, timeout=3.0)
				for msg in (msg_a, msg_b):
					if msg.get("type") != "BROADCAST":
						raise AssertionError(f"Expected BROADCAST, got {msg}")
					if msg.get("msg") != text:
						raise AssertionError(f"Expected text '{text}', got {msg.get('msg')}")
					sender = msg.get("broadcasting_user") or msg.get("user") or {}
					if sender.get("nick") != "charlie":
						raise AssertionError(f"Expected sender charlie, got {sender}")
			finally:
				conn_a.close()
				conn_b.close()

		tests = [
			("register", test_register_success),
			("register empty nick", test_register_fail_empty_nick),
			("register missing udp", test_register_fail_missing_udp),
			("broadcast without register", test_broadcast_without_register),
			("broadcast empty text", test_broadcast_empty_text),
			("message type", test_message_type_fail),
			("unknown type", test_unknown_type_fail),
			("invalid json", test_invalid_json_fail),
			("broadcast after register", test_broadcast_success_after_register),
		]

		passed = 0
		for name, fn in tests:
			if run_status_test(name, fn):
				passed += 1

		print(f"Summary: {passed}/{len(tests)} tests passed.")
		sys.exit(0 if passed == len(tests) else 1)
	finally:
		server_proc.terminate()
		try:
			server_proc.wait(timeout=2)
		except subprocess.TimeoutExpired:
			server_proc.kill()
			server_proc.wait(timeout=2)


if __name__ == "__main__":
	main()
