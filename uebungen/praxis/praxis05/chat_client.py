#!/usr/bin/env python3
import argparse
import json
import queue
import socket
import struct
import sys
import threading
import time
from dataclasses import dataclass, field

from model import Message, User


SERVER_TIMEOUT = 2.0
UDP_TIMEOUT = 0.5
PEER_WAIT_TIMEOUT = 30.0


def supports_color() -> bool:
	return sys.stdout.isatty() and sys.platform != "win32"



class Ansi:
    RESET = "\033[0m" if supports_color() else ""
    RED = "\033[31m" if supports_color() else ""
    GREEN = "\033[32m" if supports_color() else ""
    YELLOW = "\033[33m" if supports_color() else ""
    CYAN = "\033[36m" if supports_color() else ""
    MAGENTA = "\033[35m" if supports_color() else ""
    DIM = "\033[2m" if supports_color() else ""


def colorize(text: str, color: str) -> str:
	return f"{color}{text}{Ansi.RESET}" if color else text


def message2bytes(msg: Message) -> bytes:
	def to_jsonable(value):
		if isinstance(value, (str, int, float, bool)) or value is None:
			return value
		if isinstance(value, list):
			return [to_jsonable(item) for item in value]
		if hasattr(value, "__dict__"):
			return {
				key: to_jsonable(item)
				for key, item in value.__dict__.items()
				if not key.startswith("_")
			}
		return str(value)

	payload = json.dumps(to_jsonable(msg)).encode("utf-8")
	return struct.pack("!I", len(payload)) + payload


def bytes2message(payload: bytes) -> Message:
	obj = json.loads(payload.decode("utf-8"))
	message = Message()
	message.type = obj.get("type", "")
	message.msg = obj.get("msg", "")
	message.user = build_user(obj.get("user"))
	raw_userlist = obj.get("userlist", obj.get("USER_LIST", []))
	if not isinstance(raw_userlist, list):
		raw_userlist = []
	message.userlist = [build_user(item) for item in raw_userlist]
	message.broadcasting_user = build_user(obj.get("broadcasting_user"))
	if not message.broadcasting_user.nick:
		message.broadcasting_user = message.user
	return message


def build_user(data: dict | None) -> User:
	user = User()
	user.nick = ""
	user.ip_addr = ""
	user.udp_port = 0
	if data:
		user.nick = data.get("nick", "") or ""
		user.ip_addr = data.get("ip_addr", "") or ""
		udp_value = data.get("udp_port", data.get("udp", 0))
		try:
			user.udp_port = int(udp_value)
		except (TypeError, ValueError):
			user.udp_port = 0
	return user


def recv_exact(conn: socket.socket, n: int) -> bytes:
	data = b""
	while len(data) < n:
		chunk = conn.recv(n - len(data))
		if not chunk:
			raise ConnectionError("socket closed")
		data += chunk
	return data


def recv_message(conn: socket.socket, timeout: float | None = None) -> Message:
	if timeout is not None:
		conn.settimeout(timeout)
	header = recv_exact(conn, 4)
	(length,) = struct.unpack("!I", header)
	if length <= 0 or length > 1024 * 1024:
		raise ConnectionError("invalid message length")
	return bytes2message(recv_exact(conn, length))


def send_message(conn: socket.socket, msg: Message):
	conn.sendall(message2bytes(msg))


def message_from_dict(payload: dict) -> Message:
	message = Message()
	message.type = payload.get("type", "")
	message.msg = payload.get("msg", "")
	message.user = build_user(payload.get("user"))
	raw_userlist = payload.get("userlist", [])
	if isinstance(raw_userlist, list):
		message.userlist = [build_user(item) for item in raw_userlist]
	else:
		message.userlist = []
	if not message.user.nick:
		message.user.nick = payload.get("nick", "")
	return message


@dataclass
class PeerState:
	lock: threading.Lock = field(default_factory=threading.Lock)
	active: bool = False
	peer_user: User | None = None
	tcp_socket: socket.socket | None = None
	stop_event: threading.Event = field(default_factory=threading.Event)


@dataclass
class AppState:
	nick: str
	server_ip: str
	server_port: int
	bind_ip: str
	server_socket: socket.socket | None = None
	udp_socket: socket.socket | None = None
	tcp_listener: socket.socket | None = None
	local_ip: str = "127.0.0.1"
	local_udp_port: int = 0
	local_tcp_port: int = 0
	user_list: list[User] = field(default_factory=list)
	user_list_lock: threading.Lock = field(default_factory=threading.Lock)
	selected_user: User | None = None
	peer: PeerState = field(default_factory=PeerState)
	running: bool = True
	server_ready: threading.Event = field(default_factory=threading.Event)
	user_list_ready: threading.Event = field(default_factory=threading.Event)
	peer_ready: threading.Event = field(default_factory=threading.Event)
	inbound_peer_queue: queue.Queue = field(default_factory=queue.Queue)


def debug(state: AppState, text: str):
	# verbose removed: no-op
	return


def info(text: str):
	print(text)


def warn(text: str):
	print(text)


def error(text: str):
	print(colorize(text, Ansi.RED))


def local_ip_for_remote(remote_ip: str) -> str:
	probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		probe.connect((remote_ip, 9))
		return probe.getsockname()[0]
	finally:
		probe.close()


def prompt(text: str):
	try:
		return input(text)
	except EOFError:
		return ""


def print_user_list(users: list[User]):
	if not users:
		info("No users available.")
		return
	print("Available users:")
	for index, user in enumerate(users, start=1):
		print(f"  {index}. {user.nick} ({user.ip_addr}:{user.udp_port})")


def find_user_by_selection(users: list[User], value: str) -> User | None:
	value = value.strip()
	if value.isdigit():
		index = int(value) - 1
		if 0 <= index < len(users):
			return users[index]
	for user in users:
		if user.nick == value:
			return user
	return None


def server_receiver(state: AppState):
	debug(state, "server receiver started")
	try:
		while state.running:
			try:
				message = recv_message(state.server_socket)
			except socket.timeout:
				continue

			if message.type == "REGISTER_OK":
				info("Registered with server.")
				state.server_ready.set()
			elif message.type == "REGISTER_FAIL":
				error("Server rejected registration.")
				state.running = False
				state.server_ready.set()
				break
			elif message.type == "USER_LIST":
				with state.user_list_lock:
					state.user_list = list(message.userlist)
				state.user_list_ready.set()
				debug(state, f"received user list with {len(message.userlist)} entries")
				print_user_list(message.userlist)
			elif message.type == "USER_JOINED":
				with state.user_list_lock:
					state.user_list = [u for u in state.user_list if u.nick != message.user.nick]
					state.user_list.append(message.user)
				info(f"User joined: {message.user.nick}")
				print_user_list(state.user_list)
			elif message.type == "USER_LEFT":
				with state.user_list_lock:
					state.user_list = [u for u in state.user_list if u.nick != message.user.nick]
				warn(f"User left: {message.user.nick}")
				print_user_list(state.user_list)
			elif message.type == "BROADCAST":
				sender = message.broadcasting_user.nick or message.user.nick or "server"
				print(colorize(f"[broadcast] {sender}: {message.msg}", Ansi.MAGENTA))
			elif message.type == "MESSAGE_FAIL":
				error("Server reported MESSAGE_FAIL.")
			else:
				debug(state, f"unhandled server message: {message.type}")
	except (ConnectionError, OSError) as exc:
		if state.running:
			error(f"Server connection problem: {exc}")
	finally:
		state.running = False
		state.server_ready.set()
		state.user_list_ready.set()


def start_server_connection(state: AppState):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(SERVER_TIMEOUT)
	sock.connect((state.server_ip, state.server_port))
	state.server_socket = sock
	thread = threading.Thread(target=server_receiver, args=(state,), daemon=True)
	thread.start()


def udp_listener(state: AppState):
	debug(state, f"udp listener on {state.local_udp_port}")
	sock = state.udp_socket
	sock.settimeout(UDP_TIMEOUT)
	while state.running:
		try:
			payload, address = sock.recvfrom(4096)
		except socket.timeout:
			continue
		except OSError:
			break

		try:
			data = json.loads(payload.decode("utf-8"))
		except (json.JSONDecodeError, UnicodeDecodeError):
			debug(state, f"received invalid UDP payload from {address}")
			continue

		msg_type = data.get("type", "")
		if msg_type == "PEER_INVITE":
			handle_peer_invite(state, data, address)
		elif msg_type == "PEER_INVITE_ACK":
			debug(state, f"invite ack from {address}")
		else:
			debug(state, f"unknown UDP message type {msg_type} from {address}")


def start_udp_listener(state: AppState):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((state.bind_ip, state.local_udp_port))
	state.udp_socket = sock
	state.local_udp_port = sock.getsockname()[1]
	thread = threading.Thread(target=udp_listener, args=(state,), daemon=True)
	thread.start()


def peer_receiver(state: AppState, conn: socket.socket):
	debug(state, "peer receiver started")
	conn.settimeout(UDP_TIMEOUT)
	try:
		while state.running:
			try:
				message = recv_message(conn)
			except socket.timeout:
				continue

			if message.type == "MESSAGE":
				sender_nick = message.user.nick or (state.peer.peer_user.nick if state.peer.peer_user else "")
				if not message.msg or not sender_nick:
					fail = Message()
					fail.type = "MESSAGE_FAIL"
					try:
						send_message(conn, fail)
					except OSError:
						pass
					warn("Invalid peer MESSAGE received.")
					break
				sender = message.user.nick or "peer"
				print(f"{sender}: {message.msg}")
			elif message.type == "MESSAGE_FAIL":
				error("Peer reported MESSAGE_FAIL.")
			elif message.type == "DISCONNECT":
				info("Peer disconnected.")
				break
			else:
				fail = Message()
				fail.type = "MESSAGE_FAIL"
				try:
					send_message(conn, fail)
				except OSError:
					pass
				warn(f"Invalid peer message type: {message.type}")
				break
	except (ConnectionError, OSError) as exc:
		if state.running:
			warn(f"Peer connection closed: {exc}")
	finally:
		close_peer_connection(state, announce=False)


def bind_tcp_listener(state: AppState):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((state.bind_ip, 0 if state.local_tcp_port == 0 else state.local_tcp_port))
	sock.listen(1)
	sock.settimeout(0.5)
	state.tcp_listener = sock
	state.local_tcp_port = sock.getsockname()[1]


def tcp_listener_loop(state: AppState):
	debug(state, f"tcp listener on {state.local_tcp_port}")
	sock = state.tcp_listener
	while state.running:
		try:
			conn, _ = sock.accept()
		except socket.timeout:
			continue
		except OSError:
			break

		with state.peer.lock:
			if state.peer.active:
				debug(state, "rejecting extra peer connection")
				conn.close()
				continue
			state.peer.active = True
			state.peer.peer_user = state.selected_user
			state.peer.tcp_socket = conn
		state.peer_ready.set()
		print(colorize("Peer connection established.", Ansi.GREEN))
		thread = threading.Thread(target=peer_receiver, args=(state, conn), daemon=True)
		thread.start()


def start_tcp_listener(state: AppState):
	bind_tcp_listener(state)
	thread = threading.Thread(target=tcp_listener_loop, args=(state,), daemon=True)
	thread.start()


def send_peer_invite(state: AppState, target: User):
	invite = {
		"type": "PEER_INVITE",
		"user": {
			"nick": state.nick,
			"ip_addr": state.local_ip,
			"udp_port": state.local_udp_port,
		},
		"tcp_ip": state.local_ip,
		"tcp_port": state.local_tcp_port,
	}
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.sendto(json.dumps(invite).encode("utf-8"), (target.ip_addr, target.udp_port))
	finally:
		sock.close()
	debug(state, f"sent invite to {target.nick} at {target.ip_addr}:{target.udp_port}")


def handle_peer_invite(state: AppState, data: dict, address: tuple[str, int]):
	sender = build_user(data.get("user"))
	tcp_ip = data.get("tcp_ip") or sender.ip_addr or address[0]
	tcp_port = int(data.get("tcp_port", 0) or 0)
	if not sender.nick or tcp_port <= 0:
		debug(state, f"invalid peer invite from {address}")
		return

	with state.peer.lock:
		busy = state.peer.active
	if busy:
		warn(f"Busy, ignoring invite from {sender.nick}")
		return

	state.selected_user = sender

	info(f"Invite from {sender.nick} received.")
	ack = {
		"type": "PEER_INVITE_ACK",
		"user": {
			"nick": state.nick,
			"ip_addr": state.local_ip,
			"udp_port": state.local_udp_port,
		},
	}
	try:
		state.udp_socket.sendto(json.dumps(ack).encode("utf-8"), address)
	except OSError:
		warn("Could not send UDP ACK.")
		return

	try:
		peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		peer_sock.settimeout(5.0)
		peer_sock.connect((tcp_ip, tcp_port))
		with state.peer.lock:
			state.peer.active = True
			state.peer.peer_user = sender
			state.peer.tcp_socket = peer_sock
		state.peer_ready.set()
		print(colorize(f"Connected to {sender.nick}.", Ansi.GREEN))
		thread = threading.Thread(target=peer_receiver, args=(state, peer_sock), daemon=True)
		thread.start()
	except OSError as exc:
		error(f"Failed to connect back to {sender.nick}: {exc}")
		try:
			peer_sock.close()
		except Exception:
			pass


def wait_for_peer_connection(state: AppState):
	deadline = time.time() + PEER_WAIT_TIMEOUT
	while time.time() < deadline and state.running:
		with state.peer.lock:
			if state.peer.active and state.peer.tcp_socket is not None:
				return True
		time.sleep(0.1)
	return False


def close_peer_connection(state: AppState, announce: bool = True):
	with state.peer.lock:
		peer_sock = state.peer.tcp_socket
		state.peer.tcp_socket = None
		state.peer.active = False
		state.peer.peer_user = None
	if peer_sock is not None:
		try:
			if announce:
				try:
					disconnect = Message()
					disconnect.type = "DISCONNECT"
					send_message(peer_sock, disconnect)
				except Exception:
					pass
			peer_sock.shutdown(socket.SHUT_RDWR)
		except OSError:
			pass
		finally:
			peer_sock.close()
	state.peer_ready.clear()


def send_peer_message(state: AppState, text: str):
	with state.peer.lock:
		peer_sock = state.peer.tcp_socket
		peer_user = state.peer.peer_user
	if peer_sock is None or peer_user is None:
		error("No active peer connection.")
		return

	message = Message()
	message.type = "MESSAGE"
	message.user = build_user({"nick": state.nick, "ip_addr": state.local_ip, "udp_port": state.local_udp_port})
	message.msg = text
	try:
		send_message(peer_sock, message)
	except OSError as exc:
		error(f"Could not send peer message: {exc}")
		close_peer_connection(state, announce=False)


def send_server_broadcast(state: AppState, text: str):
	message = Message()
	message.type = "BROADCAST"
	message.user = build_user({"nick": state.nick, "ip_addr": state.local_ip, "udp_port": state.local_udp_port})
	message.msg = text
	try:
		send_message(state.server_socket, message)
	except OSError as exc:
		error(f"Could not send broadcast: {exc}")


def handle_command(state: AppState, line: str) -> bool:
	command, _, argument = line[1:].partition(" ")
	command = command.strip().lower()
	argument = argument.strip()

	if command in {"disconnect", "quit", "exit"}:
		close_peer_connection(state)
		if command == "disconnect":
			info("Disconnected from peer.")
			return True
		state.running = False
		info("Shutting down client.")
		return True
	if command == "broadcast":
		if not argument:
			warn("Usage: /broadcast <text>")
			return False
		send_server_broadcast(state, argument)
		return False
	if command == "help":
		print("Commands: /broadcast <text>, /disconnect, /help")
		return False

	warn(f"Unknown command: /{command}")
	return False


def register_with_server(state: AppState):
	register = Message()
	register.type = "REGISTER"
	register.user = build_user({"nick": state.nick, "ip_addr": state.local_ip, "udp_port": state.local_udp_port})
	send_message(state.server_socket, register)
	debug(state, "REGISTER sent")


def choose_user(state: AppState) -> User | None:
	while state.running:
		with state.peer.lock:
			if state.peer.active and state.peer.peer_user is not None:
				return state.peer.peer_user
		with state.user_list_lock:
			candidates = [user for user in state.user_list if user.nick != state.nick]
		if not candidates:
			warn("No other users available yet. Waiting for user list updates...")
			time.sleep(1.0)
			continue

		print_user_list(candidates)
		choice = prompt("Select user by number or nick: ").strip()
		if not choice:
			continue
		selected = find_user_by_selection(candidates, choice)
		if selected is None:
			warn("Invalid selection.")
			continue
		state.selected_user = selected
		return selected

	return None


def chat_loop(state: AppState):
	info("Entering chat mode. Commands: /broadcast <text>, /disconnect, /help")
	while state.running:
		line = prompt(f"[{state.nick}]> ").strip()
		if line == "":
			continue
		if line.startswith("/"):
			if handle_command(state, line):
				return
			continue

		with state.peer.lock:
			active = state.peer.active
		if not active:
			warn("No active peer connection.")
			continue
		send_peer_message(state, line)


def init_state(args) -> AppState:
	state = AppState(
		nick=args.nick,
		server_ip=args.server_ip,
		server_port=args.server_port,
		bind_ip=args.bind_ip,
	)
	state.local_ip = local_ip_for_remote(state.server_ip)
	return state


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--server-ip", default="127.0.0.1")
	parser.add_argument("--server-port", type=int, default=50001)
	parser.add_argument("--nick", default="")
	parser.add_argument("--bind-ip", default="0.0.0.0")
	return parser.parse_args()


def main():
	args = parse_args()
	if not args.nick:
		args.nick = prompt("Nickname: ").strip()
	if not args.nick:
		error("Nickname is required.")
		sys.exit(1)

	state = init_state(args)
	start_udp_listener(state)
	start_tcp_listener(state)
	start_server_connection(state)
	register_with_server(state)

	if not state.server_ready.wait(timeout=5.0):
		error("Server registration did not complete in time.")
		sys.exit(1)

	if not state.running:
		sys.exit(1)

	if not state.user_list_ready.wait(timeout=5.0):
		warn("Did not receive user list in time, continuing anyway.")

	while state.running:
		selected = choose_user(state)
		if selected is None:
			break

		info(f"Selected user: {selected.nick}")
		state.selected_user = selected
		with state.peer.lock:
			peer_is_active = state.peer.active and state.peer.tcp_socket is not None
		if not peer_is_active:
			send_peer_invite(state, selected)
			info("Waiting for peer connection...")
			if not wait_for_peer_connection(state):
				error("Peer connection did not establish in time.")
				continue
		else:
			info("Peer session is already active.")

		chat_loop(state)
		close_peer_connection(state, announce=False)

	state.running = False
	close_peer_connection(state, announce=False)
	try:
		if state.udp_socket is not None:
			state.udp_socket.close()
	except OSError:
		pass
	try:
		if state.tcp_listener is not None:
			state.tcp_listener.close()
	except OSError:
		pass
	try:
		if state.server_socket is not None:
			state.server_socket.close()
	except OSError:
		pass


if __name__ == "__main__":
	main()
