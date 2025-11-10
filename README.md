# Fibonacci Concurrency Test

Performance testing for different Python concurrency approaches using Fibonacci calculation servers.

Based on the article: [Python Concurrency: The Definitive Guide](https://newvick.com/posts/python-concurrency/)

## Setup

```bash
source venv/bin/activate
```

## Available servers

```bash
python server.py                    # Sequential
python server_with_thread.py        # Multi-threaded
python server_with_processes.py     # Process pool (concurrent.futures)
python server_with_asyncio.py       # Asyncio
python server_with_multiprocess.py  # Multi-process (process per connection)
python server_with_mp_pool.py       # Multi-process pool
python server_with_mp_queue.py      # Multi-process with queues
```

## Performance tests

```bash
python perf1.py      # Response time test (Fibonacci 30)
python perf2.py      # Throughput test (Fibonacci 1)
python benchmark.py  # Complete benchmark
```

## Protocol

- Port: localhost:25000
- Input: Fibonacci number as ASCII
- Output: result as ASCII + newline