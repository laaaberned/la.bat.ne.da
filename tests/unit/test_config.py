"""
Tests for configuration system.
"""

import pytest
from pathlib import Path
from beat_sync_func.core.config import Config, AudioConfig, VideoConfig


def test_config_defaults():
    """Test default configuration."""
    cfg = Config()
    assert cfg.project_name == "BEAT SYNC FUNC"
    assert cfg.version == "0.1.0"
    assert cfg.audio.sample_rate == 44100
    assert cfg.video.fps == 30


def test_audio_config_validation():
    """Test audio config validation."""
    # Valid config
    cfg = AudioConfig()
    cfg.validate()  # Should not raise
    
    # Invalid n_fft
    cfg = AudioConfig(n_fft=256, hop_length=512)
    with pytest.raises(ValueError):
        cfg.validate()


def test_video_config_validation():
    """Test video config validation."""
    # Valid config
    cfg = VideoConfig()
    cfg.validate()  # Should not raise
    
    # Invalid FPS
    cfg = VideoConfig(fps=-1)
    with pytest.raises(ValueError):
        cfg.validate()


def test_effects_config_validation():
    """Test effects config validation."""
    from beat_sync_func.core.config import EffectsConfig
    
    # Valid config
    cfg = EffectsConfig()
    cfg.validate()  # Should not raise
    
    # Invalid intensity
    cfg = EffectsConfig(effect_intensity=3.0)
    with pytest.raises(ValueError):
        cfg.validate()