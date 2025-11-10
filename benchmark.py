#!/usr/bin/env python3

import subprocess
import time
import socket
import threading
import sys
import os
import signal
import psutil
from statistics import mean

class ResourceMonitor:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.process_count_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, server_pid):
        self.reset()
        self.monitoring = True
        self.server_pid = server_pid
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        while self.monitoring:
            try:
                # Get server process and its children
                server_process = psutil.Process(self.server_pid)
                children = server_process.children(recursive=True)
                all_processes = [server_process] + children
                
                # Calculate total CPU and memory (with interval for accurate reading)
                total_cpu = sum(p.cpu_percent(interval=0.1) for p in all_processes if p.is_running())
                total_memory = sum(p.memory_info().rss for p in all_processes if p.is_running()) / 1024 / 1024  # MB
                process_count = len(all_processes)
                
                self.cpu_samples.append(total_cpu)
                self.memory_samples.append(total_memory)
                self.process_count_samples.append(process_count)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            # Note: cpu_percent(interval=0.1) already provides the delay
    
    def get_stats(self):
        if not self.cpu_samples:
            return {"avg_cpu": 0, "max_cpu": 0, "avg_memory": 0, "max_memory": 0, "max_processes": 0}
        
        return {
            "avg_cpu": mean(self.cpu_samples),
            "max_cpu": max(self.cpu_samples),
            "avg_memory": mean(self.memory_samples),
            "max_memory": max(self.memory_samples),
            "max_processes": max(self.process_count_samples)
        }

def force_kill_port_users(port):
    """Force kill all processes using a specific port"""
    try:
        result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"  Killed process {pid} using port {port}")
                except:
                    pass
            time.sleep(0.5)  # Give time for cleanup
    except:
        pass

def wait_for_port_free(port, timeout=10):
    """Wait for a port to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        try:
            result = sock.connect_ex(("localhost", port))
            if result != 0:  # Connection failed, port is free
                sock.close()
                return True
        except:
            pass
        finally:
            sock.close()
        time.sleep(0.1)
    return False

def test_server(server_script, test_duration=3):
    """Test a server implementation for both latency and throughput"""
    print(f"\n=== Testing {server_script} ===")
    
    # Ensure port is free before starting
    if not wait_for_port_free(25000, timeout=2):
        print(f"  Port 25000 in use, force cleaning...")
        force_kill_port_users(25000)
        if not wait_for_port_free(25000, timeout=3):
            print(f"  Error: Port 25000 still in use after cleanup, skipping {server_script}")
            return float('inf'), 0
    
    # Start server
    try:
        server_process = subprocess.Popen([sys.executable, server_script])
        time.sleep(1)  # Give server more time to start
        
        # Initialize resource monitoring
        monitor = ResourceMonitor()
        
        # Test 1: Latency for CPU-intensive task (fib 30)
        latencies = []
        print("Testing latency (fib 30)...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(("localhost", 25000))
            
            for _ in range(5):  # 5 samples
                start = time.time()
                sock.send(b"30")
                resp = sock.recv(100)
                end = time.time()
                latencies.append(end - start)
                
            sock.close()
            avg_latency = mean(latencies)
            print(f"  Average latency: {avg_latency:.3f}s")
            
        except Exception as e:
            print(f"  Latency test failed: {e}")
            avg_latency = float('inf')
        
        # Test 2: Throughput for CPU-intensive requests (fib 25)
        print("Testing throughput (fib 25)...")
        request_count = 0
        
        # Start resource monitoring during throughput test
        monitor.start_monitoring(server_process.pid)
        
        def throughput_test():
            nonlocal request_count
            end_time = time.time() + test_duration
            
            while time.time() < end_time:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(("localhost", 25000))
                    sock.send(b"25")
                    resp = sock.recv(100)
                    sock.close()
                    request_count += 1
                except Exception as e:
                    # Connection failed, likely due to server being busy
                    try:
                        sock.close()
                    except:
                        pass
                    time.sleep(0.001)  # Brief pause before retry
        
        try:
            # Run multiple concurrent clients
            threads = []
            for _ in range(10):  # 10 concurrent clients
                t = threading.Thread(target=throughput_test)
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()
                
            throughput = request_count / test_duration
            print(f"  Throughput: {throughput:.1f} req/sec")
            
        except Exception as e:
            print(f"  Throughput test failed: {e}")
            throughput = 0
        finally:
            # Stop monitoring and get resource stats
            monitor.stop_monitoring()
            
        resource_stats = monitor.get_stats()
        print(f"  Resources: CPU {resource_stats['avg_cpu']:.1f}% (max {resource_stats['max_cpu']:.1f}%), "
              f"Memory {resource_stats['avg_memory']:.1f}MB (max {resource_stats['max_memory']:.1f}MB), "
              f"Max processes: {resource_stats['max_processes']}")
            
        return avg_latency, throughput, resource_stats
        
    finally:
        # Clean up
        try:
            server_process.terminate()
            server_process.wait(timeout=2)
        except:
            server_process.kill()
        
        # Force clean port
        force_kill_port_users(25000)
        
        # Wait for port to be released
        if not wait_for_port_free(25000, timeout=3):
            print(f"  Warning: Port 25000 still in use after cleanup")


def main():
    servers = [
        "server.py",
        "server_with_thread.py", 
        "server_with_asyncio.py",
        "server_with_processes.py",
        "server_with_multiprocess.py",
        "server_with_mp_pool.py",
        # "server_with_mp_queue.py"  # Skip complex one for now
    ]
    
    results = {}
    
    for server in servers:
        try:
            latency, throughput, resources = test_server(server)
            results[server] = (latency, throughput, resources)
        except Exception as e:
            print(f"Failed to test {server}: {e}")
            results[server] = (float('inf'), 0, {"avg_cpu": 0, "max_cpu": 0, "avg_memory": 0, "max_memory": 0, "max_processes": 0})
        
        time.sleep(2)  # Pause between tests to ensure cleanup
    
    # Summary
    print(f"\n{'='*80}")
    print("BENCHMARK RESULTS")
    print(f"{'='*80}")
    print(f"{'Server':<25} {'Latency':<8} {'Throughput':<12} {'Avg CPU':<8} {'Max Mem':<8} {'Max Proc':<8}")
    print(f"{'':25} {'(s)':<8} {'(req/s)':<12} {'(%)':<8} {'(MB)':<8} {'(#)':<8}")
    print("-" * 80)
    
    for server, (latency, throughput, resources) in results.items():
        lat_str = f"{latency:.3f}" if latency != float('inf') else "FAIL"
        print(f"{server:<25} {lat_str:<8} {throughput:<12.1f} {resources['avg_cpu']:<8.1f} {resources['max_memory']:<8.1f} {resources['max_processes']:<8}")
    
    # Winners
    best_latency = min((lat for lat, _, _ in results.values() if lat != float('inf')), default=float('inf'))
    best_throughput = max(thr for _, thr, _ in results.values())
    
    lat_winner = [srv for srv, (lat, _, _) in results.items() if lat == best_latency][0]
    thr_winner = [srv for srv, (_, thr, _) in results.items() if thr == best_throughput][0]
    
    print(f"\n🏆 Best Latency: {lat_winner} ({best_latency:.3f}s)")
    print(f"🏆 Best Throughput: {thr_winner} ({best_throughput:.1f} req/s)")


if __name__ == "__main__":
    try:
        main()
    finally:
        # Final cleanup - make sure no processes are left using the port
        print("\nFinal cleanup...")
        force_kill_port_users(25000)