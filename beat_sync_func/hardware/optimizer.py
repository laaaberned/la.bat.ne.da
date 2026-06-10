"""
Hardware-based optimization and configuration.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from loguru import logger
import torch
import psutil

from beat_sync_func.hardware.detector import SystemInfo
from beat_sync_func.core.config import Config


class HardwareTier(Enum):
    """Hardware capability tiers."""
    LEGACY = "legacy"  # Pentium III era, < 1GB RAM
    LOW = "low"  # < 4GB RAM, no GPU
    MEDIUM = "medium"  # 4-8GB RAM, CPU-only or weak GPU
    HIGH = "high"  # 8-16GB RAM, good GPU
    ULTRA = "ultra"  # > 16GB RAM, high-end GPU


@dataclass
class OptimizationProfile:
    """Hardware-specific optimization settings."""
    
    tier: HardwareTier
    max_workers: int
    batch_size: int
    frame_sample_count: int
    use_gpu: bool
    use_mixed_precision: bool
    use_quantization: bool
    memory_limit_mb: int
    video_resolution_scale: float
    audio_quality_reduction: float
    enable_audio_compression: bool
    enable_video_compression: bool
    effect_quality: float  # 0.1 (low) to 1.0 (high)
    render_threads: int
    cache_frames: bool


class HardwareOptimizer:
    """Optimize configuration based on hardware capabilities."""
    
    def __init__(self, system_info: SystemInfo):
        """Initialize optimizer with system information."""
        self.system_info = system_info
        self.tier = self._determine_tier()
        self.profile = None
    
    def _determine_tier(self) -> HardwareTier:
        """Determine hardware tier based on system specs."""
        ram_gb = self.system_info.ram_total_gb
        has_gpu = self.system_info.has_gpu
        cpu_cores = self.system_info.cpu.cores_logical
        
        if ram_gb < 1:
            return HardwareTier.LEGACY
        elif ram_gb < 4:
            return HardwareTier.LOW
        elif ram_gb < 8:
            if has_gpu:
                return HardwareTier.MEDIUM
            return HardwareTier.LOW
        elif ram_gb < 16:
            if has_gpu:
                return HardwareTier.HIGH
            return HardwareTier.MEDIUM
        else:
            if has_gpu and cpu_cores >= 8:
                return HardwareTier.ULTRA
            return HardwareTier.HIGH
    
    def generate_profile(self) -> OptimizationProfile:
        """Generate optimization profile based on hardware tier."""
        
        logger.info(f"🔧 Generating optimization profile for {self.tier.value} hardware")
        
        tier = self.tier
        ram_gb = self.system_info.ram_total_gb
        cpu_cores = self.system_info.cpu.cores_logical
        has_gpu = self.system_info.has_gpu
        
        profiles = {
            HardwareTier.LEGACY: OptimizationProfile(
                tier=HardwareTier.LEGACY,
                max_workers=1,
                batch_size=1,
                frame_sample_count=5,
                use_gpu=False,
                use_mixed_precision=False,
                use_quantization=True,
                memory_limit_mb=256,
                video_resolution_scale=0.25,
                audio_quality_reduction=0.5,
                enable_audio_compression=True,
                enable_video_compression=True,
                effect_quality=0.2,
                render_threads=1,
                cache_frames=False,
            ),
            HardwareTier.LOW: OptimizationProfile(
                tier=HardwareTier.LOW,
                max_workers=max(1, cpu_cores // 2),
                batch_size=4,
                frame_sample_count=10,
                use_gpu=False,
                use_mixed_precision=False,
                use_quantization=True,
                memory_limit_mb=512,
                video_resolution_scale=0.5,
                audio_quality_reduction=0.3,
                enable_audio_compression=True,
                enable_video_compression=True,
                effect_quality=0.4,
                render_threads=2,
                cache_frames=False,
            ),
            HardwareTier.MEDIUM: OptimizationProfile(
                tier=HardwareTier.MEDIUM,
                max_workers=cpu_cores,
                batch_size=8,
                frame_sample_count=20,
                use_gpu=has_gpu,
                use_mixed_precision=has_gpu,
                use_quantization=False,
                memory_limit_mb=1024,
                video_resolution_scale=0.75,
                audio_quality_reduction=0.1,
                enable_audio_compression=False,
                enable_video_compression=True,
                effect_quality=0.6,
                render_threads=4,
                cache_frames=has_gpu,
            ),
            HardwareTier.HIGH: OptimizationProfile(
                tier=HardwareTier.HIGH,
                max_workers=cpu_cores,
                batch_size=16,
                frame_sample_count=30,
                use_gpu=has_gpu,
                use_mixed_precision=has_gpu,
                use_quantization=False,
                memory_limit_mb=2048,
                video_resolution_scale=1.0,
                audio_quality_reduction=0.0,
                enable_audio_compression=False,
                enable_video_compression=False,
                effect_quality=0.9,
                render_threads=8,
                cache_frames=True,
            ),
            HardwareTier.ULTRA: OptimizationProfile(
                tier=HardwareTier.ULTRA,
                max_workers=cpu_cores,
                batch_size=32,
                frame_sample_count=30,
                use_gpu=True,
                use_mixed_precision=True,
                use_quantization=False,
                memory_limit_mb=4096,
                video_resolution_scale=1.0,
                audio_quality_reduction=0.0,
                enable_audio_compression=False,
                enable_video_compression=False,
                effect_quality=1.0,
                render_threads=cpu_cores,
                cache_frames=True,
            ),
        }
        
        self.profile = profiles[tier]
        logger.info(f"✅ Optimization profile generated: {self.profile}")
        return self.profile
    
    def apply_to_config(self, config: Config) -> Config:
        """Apply optimization profile to configuration."""
        if not self.profile:
            self.generate_profile()
        
        profile = self.profile
        
        logger.info("🔧 Applying hardware optimizations to config...")
        
        # Apply optimizations
        config.num_workers = profile.max_workers
        config.video.max_frame_sample = profile.frame_sample_count
        config.use_gpu = profile.use_gpu and self.system_info.has_gpu
        config.debug_mode = False  # Disable debug for performance
        
        # Audio optimizations
        if profile.audio_quality_reduction > 0:
            config.audio.sample_rate = int(44100 * (1 - profile.audio_quality_reduction))
        
        # Video optimizations
        if profile.video_resolution_scale < 1.0:
            config.video.resolution = (
                int(1920 * profile.video_resolution_scale),
                int(1080 * profile.video_resolution_scale)
            )
        
        # Effects optimizations
        config.effects.effect_intensity = profile.effect_quality
        if profile.effect_quality < 0.5:
            config.effects.enable_time_warps = False
            config.effects.time_warp_probability = 0.0
        
        logger.info("✅ Hardware optimizations applied")
        return config
    
    def get_memory_estimate(self, duration_seconds: float, num_clips: int) -> Dict[str, float]:
        """Estimate memory usage for video processing."""
        
        # Base memory for Python + libraries
        base_mb = 300
        
        # Audio memory (44.1kHz, stereo, float32)
        audio_mb = (duration_seconds * 44100 * 4) / (1024**2)
        
        # Video memory (assume 5 clips, full HD)
        # Sample 30 frames per clip
        frames_per_clip = min(30, int(duration_seconds * 30))
        frame_size_mb = (1920 * 1080 * 3 * frames_per_clip) / (1024**2)
        video_mb = num_clips * frame_size_mb
        
        # Processing overhead
        processing_mb = 100 + (duration_seconds * 10)
        
        total_mb = base_mb + audio_mb + video_mb + processing_mb
        
        return {
            'base': base_mb,
            'audio': audio_mb,
            'video': video_mb,
            'processing': processing_mb,
            'total': total_mb,
            'estimated_peak_mb': total_mb * 1.5,  # 50% overhead
        }
    
    def get_processing_time_estimate(self, duration_seconds: float) -> Dict[str, float]:
        """Estimate processing time."""
        
        # Base times for each step (in seconds)
        base_times = {
            'audio_analysis': 2 + (duration_seconds * 0.5),
            'video_analysis': 3 + (duration_seconds * 0.1),
            'timeline_generation': 1,
            'effect_composition': 2,
            'rendering': max(10, duration_seconds * 0.5),
        }
        
        # Apply speedup based on hardware
        if self.tier == HardwareTier.LEGACY:
            speedup = 0.2
        elif self.tier == HardwareTier.LOW:
            speedup = 0.5
        elif self.tier == HardwareTier.MEDIUM:
            speedup = 1.0
        elif self.tier == HardwareTier.HIGH:
            speedup = 2.0
        else:  # ULTRA
            speedup = 4.0
        
        if self.system_info.has_gpu:
            speedup *= 1.5  # GPU bonus
        
        adjusted_times = {k: v / speedup for k, v in base_times.items()}
        adjusted_times['total'] = sum(adjusted_times.values())
        
        return adjusted_times


from typing import Dict
