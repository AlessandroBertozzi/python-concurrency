from socket import *
from fib import fib
import multiprocessing as mp


def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print("Connection", addr)
        process = mp.Process(target=fib_handler, args=(client,))
        process.start()
        client.close()  # Close in parent process, child has its own copy


def fib_handler(client):
    while True:
        req = client.recv(100)
        if not req:
            break
        result = fib(int(req))
        resp = str(result).encode("ascii") + b"\n"
        client.send(resp)
    print("Process finished")
    client.close()


if __name__ == "__main__":
    fib_server(("", 25000))