"""
GPU acceleration utilities.
"""

import torch
import torch.nn as nn
from loguru import logger
from typing import Optional, Tuple


class GPUAccelerator:
    """Manage GPU acceleration and memory optimization."""
    
    def __init__(self, device_id: int = 0, use_mixed_precision: bool = False):
        """Initialize GPU accelerator."""
        self.device_id = device_id
        self.device = None
        self.use_mixed_precision = use_mixed_precision
        self.scaler = None
        
        if torch.cuda.is_available():
            self.device = torch.device(f'cuda:{device_id}')
            logger.info(f"Using GPU: {torch.cuda.get_device_name(device_id)}")
            
            if use_mixed_precision:
                self.scaler = torch.cuda.amp.GradScaler()
                logger.info("Mixed precision enabled")
        else:
            self.device = torch.device('cpu')
            logger.warning("GPU not available, using CPU")
    
    def clear_cache(self):
        """Clear GPU cache to free memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.debug("GPU cache cleared")
    
    def get_memory_info(self) -> dict:
        """Get GPU memory information."""
        if not torch.cuda.is_available():
            return {
                'device': 'CPU',
                'allocated_mb': 0,
                'reserved_mb': 0,
                'free_mb': 0,
                'total_mb': 0,
            }
        
        allocated = torch.cuda.memory_allocated(self.device_id) / (1024**2)
        reserved = torch.cuda.memory_reserved(self.device_id) / (1024**2)
        total = torch.cuda.get_device_properties(self.device_id).total_memory / (1024**2)
        free = total - allocated
        
        return {
            'device': torch.cuda.get_device_name(self.device_id),
            'allocated_mb': allocated,
            'reserved_mb': reserved,
            'free_mb': free,
            'total_mb': total,
        }
    
    def monitor_memory(self, threshold_mb: float = 100) -> bool:
        """Monitor GPU memory and warn if low."""
        if not torch.cuda.is_available():
            return True
        
        info = self.get_memory_info()
        if info['free_mb'] < threshold_mb:
            logger.warning(f"Low GPU memory: {info['free_mb']:.0f}MB remaining")
            self.clear_cache()
            return False
        return True
    
    def to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move tensor to device."""
        if self.device:
            return tensor.to(self.device)
        return tensor
    
    def enable_cudnn_benchmark(self):
        """Enable cuDNN benchmarking for faster operations."""
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            logger.info("cuDNN benchmarking enabled")
    
    def optimize_models(self, model: nn.Module) -> nn.Module:
        """Apply optimization techniques to model."""
        if not torch.cuda.is_available():
            return model
        
        model = model.to(self.device)
        
        if self.use_mixed_precision:
            model = model.half()  # Convert to float16
        
        return model


class CPUOptimizer:
    """Optimize CPU performance."""
    
    @staticmethod
    def optimize_threading(num_threads: int):
        """Set optimal number of threads."""
        import os
        
        os.environ['OMP_NUM_THREADS'] = str(num_threads)
        os.environ['MKL_NUM_THREADS'] = str(num_threads)
        
        try:
            torch.set_num_threads(num_threads)
        except:
            pass
        
        logger.info(f"CPU threads set to {num_threads}")
    
    @staticmethod
    def optimize_libraries():
        """Optimize library settings for CPU."""
        # Disable GPU for NumPy operations
        import numpy as np
        
        # Enable SIMD optimizations
        try:
            np.set_printoptions(threshold=np.inf)
        except:
            pass
        
        logger.info("CPU optimizations applied")
