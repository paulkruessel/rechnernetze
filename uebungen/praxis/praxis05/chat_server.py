#!/usr/bin/env python3
import argparse
import socket
import struct
import json
from threading import Thread, Lock
from model import Message, User
import sys
import traceback

RUNNING = True


def supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and sys.platform != "win32"


class Ansi:
    RESET = "\033[0m" if supports_color() else ""
    RED = "\033[31m" if supports_color() else ""
    GREEN = "\033[32m" if supports_color() else ""
    YELLOW = "\033[33m" if supports_color() else ""
    CYAN = "\033[36m" if supports_color() else ""


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Ansi.RESET}" if color else text


def debug(msg: str):
    # verbose removed: no-op
    return


def info(msg: str):
    # keep plain info output
    print(msg)


def warn(msg: str):
    # keep plain warnings (no color)
    print(msg)


def error(msg: str):
    # always colorize errors
    print(colorize(msg, Ansi.RED))


active_connections = {}
user_list: list[User] = []
connections_lock = Lock()

# Helper Method to turn a Message Object into sendable bytes
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

# Helper Method to turn received bytes into a Message Object
def bytes2message(payload: bytes) -> Message:
    obj = json.loads(payload.decode("utf-8"))

    message = Message()
    message.type = obj.get("type", "")
    message.msg = obj.get("msg", "")
    message.user = build_user(obj.get("user"))

    raw_userlist = obj.get("userlist", [])
    if not isinstance(raw_userlist, list):
        raw_userlist = []
    message.userlist = [build_user(item) for item in raw_userlist]

    message.broadcasting_user = build_user(obj.get("broadcasting_user"))

    if not message.user.nick:
        message.user.nick = obj.get("nick", "")
    if not message.user.ip_addr:
        message.user.ip_addr = obj.get("ip_addr", "")
    if not message.user.udp_port:
        try:
            message.user.udp_port = int(obj.get("udp", obj.get("udp_port", 0)))
        except (TypeError, ValueError):
            message.user.udp_port = 0

    if not message.broadcasting_user.nick:
        message.broadcasting_user = message.user

    return message

# Helper Method to create a user out of a dictionary
def build_user(data: dict | None) -> User:
    user = User()
    user.nick = ""
    user.ip_addr = ""
    user.udp_port = 0
    if data:
        user.nick = data.get("nick", "")
        user.ip_addr = data.get("ip_addr", "")
        udp_value = data.get("udp_port", data.get("udp", 0))
        try:
            user.udp_port = int(udp_value)
        except (TypeError, ValueError):
            user.udp_port = 0
    return user

def create_register_ok_message(server_user: User) -> Message:
    debug("Sending REGISTER_OK")
    m = Message()
    m.type = "REGISTER_OK"
    m.user = server_user
    return m

def create_register_fail_message(server_user: User) -> Message:
    warn(f"REGISTER_FAIL for {server_user.nick}")
    m = Message()
    m.type = "REGISTER_FAIL"
    m.user = server_user
    return m


def create_message_fail_message(server_user: User) -> Message:
    warn("MESSAGE_FAIL created")
    m = Message()
    m.type = "MESSAGE_FAIL"
    m.user = server_user
    return m

def create_new_user_message(new_user: User) -> Message:
    debug(f"New user joined: {new_user.nick} {new_user.ip_addr}:{new_user.udp_port}")
    m = Message()
    m.type = "USER_JOINED"
    m.user = new_user
    return m

def create_user_disconnect_message(disconnected_user: User) -> Message:
    debug(f"User disconnected: {disconnected_user.nick} {disconnected_user.ip_addr}:{disconnected_user.udp_port}")
    m = Message()
    m.type = "USER_LEFT"
    m.user = disconnected_user
    return m


def create_user_list_message(server_user: User) -> Message:
    debug("Sending USER_LIST")
    m  = Message()
    m.type = "USER_LIST"
    m.user = server_user
    with connections_lock:
        m.userlist = list(user_list)
    return m


def create_broadcast_message(sender: User, text: str) -> Message:
    m = Message()
    m.type = "BROADCAST"
    # Keep both fields to remain compatible with stricter and looser parsers.
    m.user = sender
    m.broadcasting_user = sender
    m.msg = text
    return m


def is_valid_udp_port(value) -> bool:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return False
    return 1 <= port <= 65535


def send_fail_for_type(conn: socket.socket, server_user: User, msg_type: str):
    if msg_type == "REGISTER":
        conn.sendall(message2bytes(create_register_fail_message(server_user)))
        return
    conn.sendall(message2bytes(create_message_fail_message(server_user)))


def is_valid_message(msg: Message) -> bool:
    if not isinstance(msg.type, str) or msg.type.strip() == "":
        return False

    match msg.type:
        case "REGISTER":
            nick = (msg.user.nick or "").strip()
            return nick != "" and is_valid_udp_port(msg.user.udp_port)
        case "BROADCAST":
            return isinstance(msg.msg, str) and msg.msg.strip() != ""
        case _:
            return False


def is_registered(conn: socket.socket) -> bool:
    with connections_lock:
        return conn in active_connections


def get_registered_user(conn: socket.socket) -> User | None:
    with connections_lock:
        return active_connections.get(conn)


def nick_already_used(nick: str) -> bool:
    with connections_lock:
        return any(u.nick == nick for u in user_list)


def send_message_to_all(m: Message):
    with connections_lock:
        recipients = list(active_connections.keys())

    for conn in recipients:
        try:
            conn.sendall(message2bytes(m))
        except OSError:
            handle_disconnect(conn)

def handle_connect(conn, user):
    joined = False
    with connections_lock:
        if conn not in active_connections:
            active_connections[conn] = user
            user_list.append(user)
            joined = True

    if joined:
        send_message_to_all(create_new_user_message(user))

def handle_disconnect(conn):
    disconnected_user = None
    with connections_lock:
        disconnected_user = active_connections.get(conn)
        active_connections.pop(conn, None)
        if disconnected_user is not None and disconnected_user in user_list:
            user_list.remove(disconnected_user)

    if disconnected_user is not None:
        send_message_to_all(create_user_disconnect_message(disconnected_user))


def handle_register(conn: socket.socket, server_user: User, msg: Message):
    if is_registered(conn):
        send_fail_for_type(conn, server_user, "REGISTER")
        return False

    msg.user.nick = (msg.user.nick or "").strip()
    if msg.user.nick == "" or not is_valid_udp_port(msg.user.udp_port):
        send_fail_for_type(conn, server_user, "REGISTER")
        return False

    if nick_already_used(msg.user.nick):
        send_fail_for_type(conn, server_user, "REGISTER")
        return False

    if not msg.user.ip_addr:
        peer_ip, _ = conn.getpeername()
        msg.user.ip_addr = peer_ip

    msg.user.udp_port = int(msg.user.udp_port)

    handle_connect(conn, msg.user)
    conn.sendall(message2bytes(create_register_ok_message(server_user)))
    conn.sendall(message2bytes(create_user_list_message(server_user)))
    return True

def handle_message(conn: socket.socket, server_user: User, msg: Message):
    if not is_valid_message(msg):
        send_fail_for_type(conn, server_user, msg.type)
        return

    match msg.type:
        case "REGISTER":
            handle_register(conn, server_user, msg)
        case "BROADCAST":
            sender = get_registered_user(conn)
            if sender is None:
                send_fail_for_type(conn, server_user, msg.type)
                return
            broadcast = create_broadcast_message(sender, msg.msg)
            send_message_to_all(broadcast)
        case "MESSAGE":
            send_fail_for_type(conn, server_user, msg.type)
        case _:
            send_fail_for_type(conn, server_user, msg.type)
            

def recv_exact(conn, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket Closed")
        data += chunk
    return data


def receive_json_message(conn: socket.socket) -> Message:
    header = recv_exact(conn, 4)
    (json_len,) = struct.unpack("!I", header)
    if json_len <= 0 or json_len > 1024 * 1024:
        raise ConnectionError("Invalid JSON payload length")
    payload = recv_exact(conn, json_len)
    return bytes2message(payload)

# Helper function to read out package length and then parse bytes into message object
def receive_message(conn: socket.socket):

    server_user = User()
    server_user.ip_addr, server_user.udp_port = conn.getsockname()
    server_user.nick = "SERVER"
    try:
        while RUNNING:
            user_message = receive_json_message(conn)
            handle_message(conn, server_user, user_message)
    except (json.JSONDecodeError, UnicodeDecodeError, struct.error):
        try:
            conn.sendall(message2bytes(create_message_fail_message(server_user)))
        except OSError:
            pass
        except (ConnectionError, OSError) as e:
            error(f"Socket error: {e}")
            traceback.print_exc()
    finally:
        handle_disconnect(conn)
        conn.close()

    

# Helper function to turn the response data into bytes
def create_response(task_id: int, result: int) -> bytes:
    return struct.pack("!Ii", task_id, result)

# Function to start listening on incoming connections
def listen(sock: socket.socket):
    global RUNNING
    
    while RUNNING:
        try:
            conn, _ = sock.accept()
            Thread(target=receive_message, args=(conn,), daemon=True).start()
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
    parser.add_argument("--verbose", action="store_true", help="Enable verbose colored debug output")
    args = parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

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
