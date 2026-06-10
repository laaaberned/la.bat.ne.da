"""
Hardware module for BEAT SYNC FUNC.
"""

from beat_sync_func.hardware.detector import HardwareDetector, SystemInfo, GPUInfo, CPUInfo
from beat_sync_func.hardware.optimizer import HardwareOptimizer, HardwareTier, OptimizationProfile

__all__ = [
    'HardwareDetector',
    'HardwareOptimizer',
    'SystemInfo',
    'GPUInfo',
    'CPUInfo',
    'HardwareTier',
    'OptimizationProfile',
]
