import asyncio
from socket import *
from fib import fib


async def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    sock.setblocking(False)

    loop = asyncio.get_event_loop()

    while True:
        client, addr = await loop.sock_accept(sock)
        print("Connection", addr)
        loop.create_task(fib_handler(client, loop))


async def fib_handler(client, loop):
    while True:
        req = await loop.sock_recv(client, 100)
        if not req:
            break
        result = fib(int(req))
        resp = str(result).encode("ascii") + b"\n"
        await loop.sock_sendall(client, resp)
    client.close()


if __name__ == "__main__":
    asyncio.run(fib_server(("", 25000)))