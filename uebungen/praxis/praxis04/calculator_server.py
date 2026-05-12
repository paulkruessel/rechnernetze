import socket
import struct
from threading import Thread

socket.setdefaulttimeout(30)

my_ip = "127.0.0.1"
my_port = 50001

running = True


def create_message(task_id, result):
    message = struct.pack("!I", task_id)
    message += struct.pack("!i", result)
    return message


def parse_message(message):
    offset = 0

    task_id = struct.unpack("!I", message[offset:offset+4])[0]
    offset += 4

    operation = message[offset:offset+3].decode("utf-8")
    offset += 3

    n = struct.unpack("!B", message[offset:offset+1])[0]
    offset += 1

    numbers = []
    for _ in range(n):
        z = struct.unpack("!i", message[offset:offset+4])[0]
        numbers.append(z)
        offset += 4

    return task_id, operation, n, numbers


def calculate(operation, numbers):
    match operation:
        case "SUM":
            return sum(numbers)

        case "PRO":
            result = 1
            for num in numbers:
                result *= num
            return result

        case "MIN":
            return min(numbers)

        case "MAX":
            return max(numbers)

        case _:
            return 0


def receive(conn: socket.socket, addr):
    print("Client verbunden:", addr)

    try:
        while True:
            msg = conn.recv(1024)

            if msg == b"":
                print("Client hat Verbindung geschlossen:", addr)
                break

            task_id, operation, _, numbers = parse_message(msg)

            print("Message came in:", task_id, operation, numbers)

            result = calculate(operation, numbers)

            answer = create_message(task_id, result)

            print("answering:", answer)

            conn.sendall(answer)

    except socket.timeout:
        print("Timeout bei Client:", addr)

    except Exception as e:
        print("Fehler bei Client:", addr, e)

    finally:
        conn.close()
        print("Verbindung geschlossen:", addr)


def listen(sock: socket.socket):
    global running

    while running:
        try:
            conn, addr = sock.accept()

            thread = Thread(target=receive, args=(conn, addr))
            thread.start()

        except socket.timeout:
            continue

        except KeyboardInterrupt:
            running = False
            break


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((my_ip, my_port))
    sock.listen(5)

    print(f"Server hört auf {my_ip}:{my_port}")

    try:
        listen(sock)

    finally:
        sock.close()
        print("Server beendet")


start_server()