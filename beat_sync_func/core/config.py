"""
Configuration management for BEAT SYNC FUNC.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    
    sample_rate: int = 44100
    hop_length: int = 512
    n_fft: int = 2048
    beat_detector: str = "essentia"  # essentia, librosa, aubio
    spectral_bins: int = 128


@dataclass
class VideoConfig:
    """Video processing configuration."""
    
    fps: int = 30
    resolution: tuple = field(default_factory=lambda: (1920, 1080))
    aspect_ratio: float = 16.0 / 9.0
    codec: str = "libx264"
    quality: int = 23  # CRF value (0-51, lower = better)


@dataclass
class CutterConfig:
    """Cutting/director engine configuration."""
    
    min_cut_duration: float = 0.5  # seconds
    max_cut_duration: float = 8.0
    transition_duration: float = 0.3
    pattern_library: str = "default"
    adaptive_learning: bool = True


@dataclass
class EffectsConfig:
    """Visual effects configuration."""
    
    enable_transitions: bool = True
    enable_time_warps: bool = True
    enable_zoom: bool = True
    enable_scratching: bool = True
    effect_intensity: float = 1.0  # 0.0 - 2.0
    blend_mode: str = "crossfade"


@dataclass
class Config:
    """Master configuration class."""
    
    project_name: str = "BEAT SYNC FUNC"
    version: str = "0.1.0"
    
    # Sub-configurations
    audio: AudioConfig = field(default_factory=AudioConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    cutter: CutterConfig = field(default_factory=CutterConfig)
    effects: EffectsConfig = field(default_factory=EffectsConfig)
    
    # Paths
    input_dir: Optional[str] = None
    output_dir: Optional[str] = None
    temp_dir: Optional[str] = None
    
    # Processing
    num_workers: int = 4
    use_gpu: bool = True
    debug_mode: bool = False
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Parse nested configurations
        audio_data = data.get('audio', {})
        video_data = data.get('video', {})
        cutter_data = data.get('cutter', {})
        effects_data = data.get('effects', {})
        
        config = cls(
            project_name=data.get('project_name', cls.project_name),
            version=data.get('version', cls.version),
            audio=AudioConfig(**audio_data),
            video=VideoConfig(**video_data),
            cutter=CutterConfig(**cutter_data),
            effects=EffectsConfig(**effects_data),
            input_dir=data.get('input_dir'),
            output_dir=data.get('output_dir'),
            temp_dir=data.get('temp_dir'),
            num_workers=data.get('num_workers', 4),
            use_gpu=data.get('use_gpu', True),
            debug_mode=data.get('debug_mode', False),
        )
        
        logger.info(f"✅ Configuration loaded from {config_path}")
        return config
    
    def to_yaml(self, output_path: str) -> None:
        """Save configuration to YAML file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'project_name': self.project_name,
            'version': self.version,
            'audio': {
                'sample_rate': self.audio.sample_rate,
                'hop_length': self.audio.hop_length,
                'n_fft': self.audio.n_fft,
                'beat_detector': self.audio.beat_detector,
                'spectral_bins': self.audio.spectral_bins,
            },
            'video': {
                'fps': self.video.fps,
                'resolution': self.video.resolution,
                'aspect_ratio': self.video.aspect_ratio,
                'codec': self.video.codec,
                'quality': self.video.quality,
            },
            'cutter': {
                'min_cut_duration': self.cutter.min_cut_duration,
                'max_cut_duration': self.cutter.max_cut_duration,
                'transition_duration': self.cutter.transition_duration,
                'pattern_library': self.cutter.pattern_library,
                'adaptive_learning': self.cutter.adaptive_learning,
            },
            'effects': {
                'enable_transitions': self.effects.enable_transitions,
                'enable_time_warps': self.effects.enable_time_warps,
                'enable_zoom': self.effects.enable_zoom,
                'enable_scratching': self.effects.enable_scratching,
                'effect_intensity': self.effects.effect_intensity,
                'blend_mode': self.effects.blend_mode,
            },
            'input_dir': self.input_dir,
            'output_dir': self.output_dir,
            'temp_dir': self.temp_dir,
            'num_workers': self.num_workers,
            'use_gpu': self.use_gpu,
            'debug_mode': self.debug_mode,
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"✅ Configuration saved to {output_path}")