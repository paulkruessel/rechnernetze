import socket
import struct
socket.setdefaulttimeout(30)

server_ip = "127.0.0.1"
server_port = 50001
my_ip = "127.0.0.2"
my_port = 50000

numbers = [1, 2, 3, 4, 5]
task_id = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))

def start_task(sock: socket.socket, message: bytes):
    sock.send(message)
    msg=sock.recv(1024)
    print("sent:", msg.hex())
    print("received:", msg.hex())
    print(parse_message(msg))

def create_message(task_id, operation, numbers):
    # ID: unsigned int, 4 Bytes
    # Operation: UTF-8-String, variable Länge
    # N: unsigned char, 1 Byte
    # Zahlen: signed int, je 4 Bytes

    n = len(numbers)

    message = struct.pack("!I", task_id)
    message += operation.encode("utf-8")
    message += struct.pack("!B", n)

    for z in numbers:
        message += struct.pack("!i", z)

    print("Parsed Message:", message)

    return message

def parse_message(message):
    offset = 0

    task_id = struct.unpack("!I", message[offset:offset+4])[0]
    offset += 4

    result = struct.unpack("!i", message[offset:])[0]

    return task_id, result

def get_calculation(op: str):
    start_task(sock, create_message(task_id, op, numbers))

get_calculation("SUM")
# print(sum(numbers))
# get_calculation("PRO")
# i = 1
# for n in numbers:
#     i *= n
# print(i)
# get_calculation("MIN")
# print(min(numbers))
# get_calculation("MAX")
# print(max(numbers))
# get_calculation("STO")

sock.close()

