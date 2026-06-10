"""
Tests for rendering engine.
"""

import pytest
from pathlib import Path
from beat_sync_func.rendering.ffmpeg_wrapper import FFmpegRenderer
from beat_sync_func.rendering.advanced_effects import AdvancedEffects, LUTGenerator


def test_ffmpeg_available():
    """Test if FFmpeg is available."""
    try:
        renderer = FFmpegRenderer()
        assert renderer is not None
    except RuntimeError:
        pytest.skip("FFmpeg not installed")


def test_advanced_effects():
    """Test advanced effects (require numpy/cv2)."""
    import numpy as np
    import cv2
    
    # Create test frame
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    # Test effects
    assert AdvancedEffects.apply_motion_blur(frame).shape == frame.shape
    assert AdvancedEffects.apply_chromatic_aberration(frame).shape == frame.shape
    assert AdvancedEffects.apply_film_grain(frame).shape == frame.shape


def test_lut_generation():
    """Test LUT generation."""
    
    cool_lut = LUTGenerator.create_cool_lut()
    assert cool_lut.shape == (256, 3)
    
    warm_lut = LUTGenerator.create_warm_lut()
    assert warm_lut.shape == (256, 3)
    
    cinematic_lut = LUTGenerator.create_cinematic_lut()
    assert cinematic_lut.shape == (256, 3)
