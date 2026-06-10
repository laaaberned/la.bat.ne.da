"""
Hardware detection and optimization module.
"""

import platform
import psutil
import torch
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
from loguru import logger


@dataclass
class GPUInfo:
    """GPU device information."""
    
    device_id: int
    name: str
    memory_total: int  # in MB
    memory_free: int  # in MB
    compute_capability: tuple
    is_available: bool
    driver_version: str
    cuda_version: str


@dataclass
class CPUInfo:
    """CPU device information."""
    
    name: str
    cores_physical: int
    cores_logical: int
    frequency_mhz: float
    cache_mb: int


@dataclass
class SystemInfo:
    """Complete system hardware information."""
    
    os: str
    os_version: str
    cpu: CPUInfo
    gpus: List[GPUInfo]
    ram_total_gb: float
    ram_available_gb: float
    disk_total_gb: float
    disk_available_gb: float
    has_cuda: bool
    has_gpu: bool
    python_version: str
    torch_version: str
    opencv_version: str


class HardwareDetector:
    """Detect and analyze system hardware."""
    
    def __init__(self):
        """Initialize hardware detector."""
        self.system_info = None
    
    def detect(self) -> SystemInfo:
        """Detect all hardware information."""
        logger.info("🔍 Detecting system hardware...")
        
        try:
            # Get OS info
            os_name = platform.system()
            os_version = platform.release()
            
            # Get CPU info
            cpu_info = self._detect_cpu()
            
            # Get GPU info
            gpus = self._detect_gpus()
            has_gpu = len(gpus) > 0
            has_cuda = torch.cuda.is_available()
            
            # Get RAM info
            ram_total = psutil.virtual_memory().total / (1024**3)
            ram_available = psutil.virtual_memory().available / (1024**3)
            
            # Get disk info
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)
            disk_available = disk.free / (1024**3)
            
            # Get software versions
            python_version = platform.python_version()
            torch_version = torch.__version__
            try:
                import cv2
                opencv_version = cv2.__version__
            except:
                opencv_version = "Unknown"
            
            self.system_info = SystemInfo(
                os=os_name,
                os_version=os_version,
                cpu=cpu_info,
                gpus=gpus,
                ram_total_gb=ram_total,
                ram_available_gb=ram_available,
                disk_total_gb=disk_total,
                disk_available_gb=disk_available,
                has_cuda=has_cuda,
                has_gpu=has_gpu,
                python_version=python_version,
                torch_version=torch_version,
                opencv_version=opencv_version,
            )
            
            logger.info("✅ Hardware detection complete")
            return self.system_info
            
        except Exception as e:
            logger.error(f"Hardware detection failed: {e}")
            raise
    
    def _detect_cpu(self) -> CPUInfo:
        """Detect CPU information."""
        try:
            cpu_name = platform.processor()
            cores_physical = psutil.cpu_count(logical=False) or 1
            cores_logical = psutil.cpu_count(logical=True) or 1
            frequency = psutil.cpu_freq().current
            
            # Try to get cache info (platform-specific)
            try:
                cache_mb = psutil.virtual_memory().total // (1024**2 * 100)  # Rough estimate
            except:
                cache_mb = 256  # Default estimate
            
            return CPUInfo(
                name=cpu_name,
                cores_physical=cores_physical,
                cores_logical=cores_logical,
                frequency_mhz=frequency,
                cache_mb=cache_mb,
            )
        except Exception as e:
            logger.warning(f"Could not detect CPU info: {e}")
            return CPUInfo(
                name="Unknown",
                cores_physical=1,
                cores_logical=1,
                frequency_mhz=0.0,
                cache_mb=0,
            )
    
    def _detect_gpus(self) -> List[GPUInfo]:
        """Detect GPU information."""
        gpus = []
        
        try:
            if not torch.cuda.is_available():
                logger.info("No CUDA-capable GPUs detected")
                return gpus
            
            device_count = torch.cuda.device_count()
            logger.info(f"Found {device_count} GPU(s)")
            
            for device_id in range(device_count):
                try:
                    with torch.cuda.device(device_id):
                        gpu_info = GPUInfo(
                            device_id=device_id,
                            name=torch.cuda.get_device_name(device_id),
                            memory_total=torch.cuda.get_device_properties(device_id).total_memory // (1024**2),
                            memory_free=torch.cuda.mem_get_info(device_id)[0] // (1024**2),
                            compute_capability=torch.cuda.get_device_capability(device_id),
                            is_available=True,
                            driver_version=torch.version.cuda,
                            cuda_version=torch.cuda.get_device_name(device_id),
                        )
                        gpus.append(gpu_info)
                        logger.info(f"  GPU {device_id}: {gpu_info.name} ({gpu_info.memory_total}MB)")
                except Exception as e:
                    logger.warning(f"Could not detect GPU {device_id}: {e}")
            
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")
        
        return gpus
    
    def print_summary(self):
        """Print hardware summary."""
        if not self.system_info:
            self.detect()
        
        info = self.system_info
        
        print("\n" + "="*60)
        print("🔍 SYSTEM HARDWARE INFORMATION")
        print("="*60)
        
        # OS
        print(f"\n🚪 Operating System")
        print(f"  OS: {info.os} {info.os_version}")
        print(f"  Python: {info.python_version}")
        print(f"  PyTorch: {info.torch_version}")
        print(f"  OpenCV: {info.opencv_version}")
        
        # CPU
        print(f"\n⚙️  CPU")
        print(f"  Model: {info.cpu.name}")
        print(f"  Physical Cores: {info.cpu.cores_physical}")
        print(f"  Logical Cores: {info.cpu.cores_logical}")
        print(f"  Frequency: {info.cpu.frequency_mhz:.0f} MHz")
        
        # RAM
        print(f"\n💾 Memory")
        print(f"  Total: {info.ram_total_gb:.1f} GB")
        print(f"  Available: {info.ram_available_gb:.1f} GB")
        
        # Disk
        print(f"\n🖤 Storage")
        print(f"  Total: {info.disk_total_gb:.1f} GB")
        print(f"  Available: {info.disk_available_gb:.1f} GB")
        
        # GPU
        if info.has_gpu:
            print(f"\n💻 GPU ({len(info.gpus)} device(s))")
            for gpu in info.gpus:
                print(f"  [{gpu.device_id}] {gpu.name}")
                print(f"       Memory: {gpu.memory_total} MB")
                print(f"       Compute Capability: {gpu.compute_capability[0]}.{gpu.compute_capability[1]}")
        else:
            print(f"\n💻 GPU: No CUDA-capable GPU detected")
        
        print(f"\nCUDA Available: {info.has_cuda}")
        print("="*60 + "\n")
