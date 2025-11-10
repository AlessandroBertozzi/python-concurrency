# Fibonacci Concurrency Test

Test di prestazioni per diversi approcci di concorrenza in Python con server Fibonacci.

## Setup

```bash
source venv/bin/activate
```

## Server disponibili

```bash
python server.py                    # Sequenziale
python server_with_thread.py        # Multi-thread
python server_with_processes.py     # Process pool (concurrent.futures)
python server_with_asyncio.py       # Asyncio
python server_with_multiprocess.py  # Multi-process (processo per connessione)
python server_with_mp_pool.py       # Multi-process pool
python server_with_mp_queue.py      # Multi-process con code
```

## Test di performance

```bash
python perf1.py      # Test tempo di risposta (Fibonacci 30)
python perf2.py      # Test throughput (Fibonacci 1)
python benchmark.py  # Benchmark completo
```

## Protocollo

- Porta: localhost:25000
- Input: numero Fibonacci come ASCII
- Output: risultato come ASCII + newline