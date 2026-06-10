"""
Hardware benchmarking utilities.
"""

import time
import numpy as np
from loguru import logger
from beat_sync_func.hardware.detector import HardwareDetector
from beat_sync_func.hardware.accelerator import GPUAccelerator
import torch


class HardwareBenchmark:
    """Benchmark hardware performance."""
    
    @staticmethod
    def benchmark_cpu(iterations: int = 1000) -> dict:
        """Benchmark CPU performance."""
        logger.info(f"Benchmarking CPU ({iterations} iterations)...")
        
        # Matrix multiplication benchmark
        a = np.random.randn(1000, 1000)
        b = np.random.randn(1000, 1000)
        
        start = time.time()
        for _ in range(iterations):
            np.dot(a, b)
        duration = time.time() - start
        
        gflops = (iterations * 1000 * 1000 * 2) / (duration * 1e9)
        
        logger.info(f"CPU Performance: {gflops:.2f} GFLOPS")
        
        return {
            'type': 'CPU',
            'gflops': gflops,
            'time_seconds': duration,
        }
    
    @staticmethod
    def benchmark_gpu() -> dict:
        """Benchmark GPU performance."""
        if not torch.cuda.is_available():
            logger.warning("GPU not available")
            return {'type': 'GPU', 'available': False}
        
        logger.info("Benchmarking GPU...")
        
        # Warm up
        for _ in range(3):
            a = torch.randn(1000, 1000, device='cuda')
            b = torch.randn(1000, 1000, device='cuda')
            torch.mm(a, b)
        
        torch.cuda.synchronize()
        
        # Benchmark
        start = time.time()
        for _ in range(100):
            a = torch.randn(1000, 1000, device='cuda')
            b = torch.randn(1000, 1000, device='cuda')
            torch.mm(a, b)
        torch.cuda.synchronize()
        duration = time.time() - start
        
        gflops = (100 * 1000 * 1000 * 2) / (duration * 1e9)
        
        logger.info(f"GPU Performance: {gflops:.2f} GFLOPS")
        
        return {
            'type': 'GPU',
            'available': True,
            'gflops': gflops,
            'time_seconds': duration,
            'device': torch.cuda.get_device_name(0),
        }
    
    @staticmethod
    def benchmark_memory() -> dict:
        """Benchmark memory performance."""
        logger.info("Benchmarking memory...")
        
        sizes = [1000000, 10000000, 100000000]
        results = []
        
        for size in sizes:
            a = np.zeros(size)
            
            start = time.time()
            for _ in range(100):
                a[:] = np.random.randn(size)
            duration = time.time() - start
            
            # Bandwidth in GB/s
            bandwidth = (100 * size * 8) / (duration * 1e9)
            results.append({
                'size': size,
                'bandwidth_gbps': bandwidth,
            })
        
        avg_bandwidth = np.mean([r['bandwidth_gbps'] for r in results])
        logger.info(f"Memory Bandwidth: {avg_bandwidth:.2f} GB/s")
        
        return {
            'type': 'Memory',
            'results': results,
            'avg_bandwidth_gbps': avg_bandwidth,
        }
    
    @staticmethod
    def full_benchmark() -> dict:
        """Run full hardware benchmark."""
        logger.info("\n" + "="*60)
        logger.info("🌟 HARDWARE BENCHMARK")
        logger.info("="*60)
        
        detector = HardwareDetector()
        system_info = detector.detect()
        
        results = {
            'system': system_info,
            'cpu': HardwareBenchmark.benchmark_cpu(),
            'gpu': HardwareBenchmark.benchmark_gpu(),
            'memory': HardwareBenchmark.benchmark_memory(),
        }
        
        logger.info("="*60)
        logger.info("✅ Benchmark complete")
        logger.info("="*60 + "\n")
        
        return results
