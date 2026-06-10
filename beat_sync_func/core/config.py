"""
Configuration management for BEAT SYNC FUNC.
"""

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from loguru import logger


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    
    sample_rate: int = 44100
    hop_length: int = 512
    n_fft: int = 2048
    beat_detector: str = "librosa"  # librosa, aubio
    spectral_bins: int = 128
    
    def validate(self) -> None:
        """Validate audio configuration."""
        if self.sample_rate not in [22050, 44100, 48000]:
            logger.warning(f"Unusual sample rate: {self.sample_rate}Hz")
        if self.n_fft < self.hop_length:
            raise ValueError(f"n_fft ({self.n_fft}) must be >= hop_length ({self.hop_length})")


@dataclass
class VideoConfig:
    """Video processing configuration."""
    
    fps: int = 30
    resolution: Tuple[int, int] = field(default_factory=lambda: (1920, 1080))
    aspect_ratio: float = 16.0 / 9.0
    codec: str = "libx264"
    quality: int = 23  # CRF value (0-51, lower = better)
    max_frame_sample: int = 30  # Max frames to sample for analysis
    
    def validate(self) -> None:
        """Validate video configuration."""
        if self.fps <= 0:
            raise ValueError(f"FPS must be positive, got {self.fps}")
        if any(r <= 0 for r in self.resolution):
            raise ValueError(f"Resolution must be positive, got {self.resolution}")
        if not (0 <= self.quality <= 51):
            raise ValueError(f"Quality (CRF) must be 0-51, got {self.quality}")


@dataclass
class CutterConfig:
    """Cutting/director engine configuration."""
    
    min_cut_duration: float = 0.5  # seconds
    max_cut_duration: float = 8.0
    transition_duration: float = 0.3
    pattern_library: str = "default"
    adaptive_learning: bool = True
    beat_alignment_threshold: float = 0.1
    
    def validate(self) -> None:
        """Validate cutter configuration."""
        if self.min_cut_duration <= 0:
            raise ValueError(f"min_cut_duration must be positive, got {self.min_cut_duration}")
        if self.max_cut_duration < self.min_cut_duration:
            raise ValueError(f"max_cut_duration must be >= min_cut_duration")
        if self.transition_duration < 0:
            raise ValueError(f"transition_duration must be non-negative")


@dataclass
class EffectsConfig:
    """Visual effects configuration."""
    
    enable_transitions: bool = True
    enable_time_warps: bool = True
    enable_zoom: bool = True
    enable_scratching: bool = False
    effect_intensity: float = 1.0  # 0.0 - 2.0
    blend_mode: str = "crossfade"
    transition_probability: float = 1.0
    zoom_probability: float = 0.3
    time_warp_probability: float = 0.2
    
    def validate(self) -> None:
        """Validate effects configuration."""
        if not (0.0 <= self.effect_intensity <= 2.0):
            raise ValueError(f"effect_intensity must be 0.0-2.0, got {self.effect_intensity}")
        if self.blend_mode not in ['crossfade', 'dissolve', 'wipe']:
            raise ValueError(f"Unknown blend_mode: {self.blend_mode}")
        for prob_name in ['transition_probability', 'zoom_probability', 'time_warp_probability']:
            prob_val = getattr(self, prob_name)
            if not (0.0 <= prob_val <= 1.0):
                raise ValueError(f"{prob_name} must be 0.0-1.0, got {prob_val}")


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
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate all sub-configurations."""
        try:
            self.audio.validate()
            self.video.validate()
            self.cutter.validate()
            self.effects.validate()
            logger.debug("✅ Configuration validation passed")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML config: {e}")
            return cls()
        
        # Parse nested configurations
        audio_data = data.get('audio', {})
        video_data = data.get('video', {})
        cutter_data = data.get('cutter', {})
        effects_data = data.get('effects', {})
        
        # Handle resolution which may be a list
        if isinstance(video_data.get('resolution'), list):
            video_data['resolution'] = tuple(video_data['resolution'])
        
        config = cls(
            project_name=data.get('project_name', cls.project_name),
            version=data.get('version', cls.version),
            audio=AudioConfig(**{k: v for k, v in audio_data.items() if k in AudioConfig.__dataclass_fields__}),
            video=VideoConfig(**{k: v for k, v in video_data.items() if k in VideoConfig.__dataclass_fields__}),
            cutter=CutterConfig(**{k: v for k, v in cutter_data.items() if k in CutterConfig.__dataclass_fields__}),
            effects=EffectsConfig(**{k: v for k, v in effects_data.items() if k in EffectsConfig.__dataclass_fields__}),
            input_dir=data.get('input_dir'),
            output_dir=data.get('output_dir'),
            temp_dir=data.get('temp_dir'),
            num_workers=max(1, int(data.get('num_workers', 4))),
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
            'audio': asdict(self.audio),
            'video': {**asdict(self.video), 'resolution': list(self.video.resolution)},
            'cutter': asdict(self.cutter),
            'effects': asdict(self.effects),
            'input_dir': self.input_dir,
            'output_dir': self.output_dir,
            'temp_dir': self.temp_dir,
            'num_workers': self.num_workers,
            'use_gpu': self.use_gpu,
            'debug_mode': self.debug_mode,
        }
        
        try:
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"✅ Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise