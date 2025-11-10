from socket import *
from fib import fib
import multiprocessing as mp
from threading import Thread
import json


def fib_worker(task_queue, result_queue):
    """Worker process that processes fibonacci requests"""
    while True:
        task = task_queue.get()
        if task is None:  # Poison pill
            break
        
        task_id, n = task
        result = fib(n)
        result_queue.put((task_id, result))


def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    
    # Create queues and worker processes
    num_workers = 4
    task_queue = mp.Queue()
    result_queue = mp.Queue()
    
    workers = []
    for _ in range(num_workers):
        p = mp.Process(target=fib_worker, args=(task_queue, result_queue))
        p.start()
        workers.append(p)
    
    # Start result dispatcher thread
    pending_tasks = {}
    result_thread = Thread(target=result_dispatcher, 
                          args=(result_queue, pending_tasks), 
                          daemon=True)
    result_thread.start()
    
    task_id_counter = 0
    
    try:
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            Thread(target=fib_handler, 
                  args=(client, task_queue, pending_tasks, task_id_counter), 
                  daemon=True).start()
            task_id_counter += 1000  # Give each connection a range of IDs
    finally:
        # Cleanup
        for _ in workers:
            task_queue.put(None)
        for p in workers:
            p.join()


def result_dispatcher(result_queue, pending_tasks):
    """Thread that dispatches results back to waiting clients"""
    while True:
        task_id, result = result_queue.get()
        if task_id in pending_tasks:
            client, event = pending_tasks[task_id]
            pending_tasks[task_id] = (client, event, result)
            event.set()


def fib_handler(client, task_queue, pending_tasks, base_task_id):
    """Handle client connection with multiprocessing queue"""
    local_task_id = base_task_id
    
    while True:
        req = client.recv(100)
        if not req:
            break
            
        n = int(req)
        
        # Create synchronization event
        import threading
        event = threading.Event()
        
        # Submit task
        pending_tasks[local_task_id] = (client, event)
        task_queue.put((local_task_id, n))
        
        # Wait for result
        event.wait()
        
        # Get result and send response
        _, _, result = pending_tasks[local_task_id]
        del pending_tasks[local_task_id]
        
        resp = str(result).encode("ascii") + b"\n"
        client.send(resp)
        
        local_task_id += 1
    
    print("Connection closed")
    client.close()


if __name__ == "__main__":
    fib_server(("", 25000))