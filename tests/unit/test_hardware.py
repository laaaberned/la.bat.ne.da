"""
Tests for hardware detection.
"""

import pytest
from beat_sync_func.hardware.detector import HardwareDetector
from beat_sync_func.hardware.optimizer import HardwareOptimizer, HardwareTier


def test_hardware_detection():
    """Test hardware detection."""
    detector = HardwareDetector()
    system_info = detector.detect()
    
    assert system_info is not None
    assert system_info.cpu is not None
    assert system_info.ram_total_gb > 0
    assert system_info.python_version is not None


def test_hardware_optimization():
    """Test hardware optimization."""
    detector = HardwareDetector()
    system_info = detector.detect()
    
    optimizer = HardwareOptimizer(system_info)
    profile = optimizer.generate_profile()
    
    assert profile is not None
    assert profile.max_workers > 0
    assert profile.batch_size > 0
    assert 0 <= profile.effect_quality <= 1.0


def test_memory_estimation():
    """Test memory estimation."""
    detector = HardwareDetector()
    system_info = detector.detect()
    
    optimizer = HardwareOptimizer(system_info)
    memory = optimizer.get_memory_estimate(duration_seconds=60, num_clips=10)
    
    assert memory['total'] > 0
    assert memory['estimated_peak_mb'] > memory['total']


def test_processing_time_estimation():
    """Test processing time estimation."""
    detector = HardwareDetector()
    system_info = detector.detect()
    
    optimizer = HardwareOptimizer(system_info)
    times = optimizer.get_processing_time_estimate(duration_seconds=60)
    
    assert times['total'] > 0
    assert times['rendering'] > 0
