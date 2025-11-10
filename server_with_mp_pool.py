from socket import *
from fib import fib
import multiprocessing as mp
from threading import Thread


def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    
    # Create a multiprocessing pool
    with mp.Pool(processes=4) as pool:
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            # Use thread for I/O, process pool for computation
            Thread(target=fib_handler, args=(client, pool), daemon=True).start()


def fib_handler(client, pool):
    while True:
        req = client.recv(100)
        if not req:
            break
        n = int(req)
        # Submit to process pool and wait for result
        result = pool.apply(fib, (n,))
        resp = str(result).encode("ascii") + b"\n"
        client.send(resp)
    print("Connection closed")
    client.close()


if __name__ == "__main__":
    fib_server(("", 25000))