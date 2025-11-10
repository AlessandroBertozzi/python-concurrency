# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python concurrency testing project that demonstrates different approaches to handling concurrent connections in a Fibonacci calculation server. The project compares sequential, threaded, process-based, and asyncio implementations.

## Core Architecture

### Main Components
- **fib.py**: Simple recursive Fibonacci implementation used by all servers
- **server.py**: Basic sequential server (baseline implementation)
- **server_with_thread.py**: Multi-threaded server using threading.Thread
- **server_with_processes.py**: Process pool server using concurrent.futures.ProcessPoolExecutor
- **server_with_asyncio.py**: Async server using asyncio event loop
- **server_with_multiprocess.py**: Multi-process server using multiprocessing.Process (one process per connection)
- **server_with_mp_pool.py**: Multi-process server using multiprocessing.Pool
- **server_with_mp_queue.py**: Multi-process server using multiprocessing.Queue for worker communication

### Performance Testing
- **perf1.py**: Measures response time for long-running requests (Fibonacci 30)
- **perf2.py**: Measures throughput for fast requests (Fibonacci 1) with requests/sec monitoring

## Running the Project

### Start a server
```bash
python server.py                    # Sequential server
python server_with_thread.py        # Threaded server  
python server_with_processes.py     # Process pool server (concurrent.futures)
python server_with_asyncio.py       # Async server
python server_with_multiprocess.py  # Multi-process server (Process per connection)
python server_with_mp_pool.py       # Multi-process server (Pool)
python server_with_mp_queue.py      # Multi-process server (Queue-based workers)
```

All servers listen on localhost:25000

### Run performance tests
```bash
python perf1.py    # Test response time (ensure server is running first)
python perf2.py    # Test throughput (ensure server is running first)
```

## Development Environment

The project uses a Python virtual environment located in `venv/`. Activate it with:
```bash
source venv/bin/activate  # Linux/Mac
# or 
venv\Scripts\activate     # Windows
```

## Socket Protocol

All servers implement the same simple protocol:
- Client sends Fibonacci number as ASCII bytes
- Server responds with result as ASCII + newline
- Multiple requests can be sent on same connection
- Connection closes when client disconnects

## Concurrency Patterns

1. **Sequential** (server.py): One request at a time, blocks on each calculation
2. **Threading** (server_with_thread.py): New thread per connection, shared GIL limitations
3. **ProcessPoolExecutor** (server_with_processes.py): Process pool with 4 workers using concurrent.futures
4. **Asyncio** (server_with_asyncio.py): Event loop with tasks, single-threaded but non-blocking I/O
5. **Multiprocessing.Process** (server_with_multiprocess.py): Dedicated process per connection, full isolation
6. **Multiprocessing.Pool** (server_with_mp_pool.py): Process pool using multiprocessing.Pool with blocking calls
7. **Multiprocessing.Queue** (server_with_mp_queue.py): Worker processes communicate via queues, more complex but flexible

## Multiprocessing Comparison

- **ProcessPoolExecutor**: High-level interface, future-based, automatic task distribution
- **Process per connection**: Maximum isolation, high memory overhead, no sharing between connections
- **Pool with apply()**: Lower-level than ProcessPoolExecutor, blocking calls, traditional approach
- **Queue-based workers**: Most flexible, allows complex communication patterns, producer-consumer model