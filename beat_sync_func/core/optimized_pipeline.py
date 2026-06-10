"""
Main pipeline with hardware optimization.
"""

import time
from pathlib import Path
from typing import Optional

from loguru import logger

from beat_sync_func.core.config import Config
from beat_sync_func.core.pipeline import BeatSyncPipeline
from beat_sync_func.hardware.detector import HardwareDetector
from beat_sync_func.hardware.optimizer import HardwareOptimizer
from beat_sync_func.hardware.accelerator import GPUAccelerator, CPUOptimizer
from beat_sync_func.audio.loader import AudioLoader
from beat_sync_func.audio.beat_detector import BeatDetector
from beat_sync_func.video.loader import VideoLoader
from beat_sync_func.video.analyzer import VideoAnalyzer
from beat_sync_func.cutter.director import Director
from beat_sync_func.effects.composer import EffectComposer


class OptimizedBeatSyncPipeline(BeatSyncPipeline):
    """Beat sync pipeline with hardware optimization."""
    
    def __init__(self, config: Config, detect_hardware: bool = True):
        """Initialize pipeline with optional hardware detection."""
        
        if detect_hardware:
            # Detect hardware
            detector = HardwareDetector()
            system_info = detector.detect()
            detector.print_summary()
            
            # Generate optimization profile
            optimizer = HardwareOptimizer(system_info)
            profile = optimizer.generate_profile()
            logger.info(f"💻 Hardware Tier: {profile.tier.value}")
            logger.info(f"   Workers: {profile.max_workers}")
            logger.info(f"   Batch Size: {profile.batch_size}")
            logger.info(f"   GPU Enabled: {profile.use_gpu}")
            logger.info(f"   Effect Quality: {profile.effect_quality}")
            
            # Apply optimizations to config
            config = optimizer.apply_to_config(config)
            
            # Setup GPU/CPU optimizers
            if config.use_gpu and system_info.has_gpu:
                self.gpu_accelerator = GPUAccelerator(
                    use_mixed_precision=profile.use_mixed_precision
                )
                self.gpu_accelerator.enable_cudnn_benchmark()
            else:
                self.gpu_accelerator = None
                CPUOptimizer.optimize_threading(profile.max_workers)
                CPUOptimizer.optimize_libraries()
        else:
            self.gpu_accelerator = None
        
        # Initialize parent pipeline
        super().__init__(config)
    
    def process(
        self,
        music_path: str,
        clip_pool_dir: str,
        output_path: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Process video with optimized pipeline."""
        
        start_time = time.time()
        
        try:
            # Validate inputs
            music_path = Path(music_path)
            clip_pool_dir = Path(clip_pool_dir)
            output_path = Path(output_path)
            
            if not music_path.exists():
                raise FileNotFoundError(f"Music file not found: {music_path}")
            if not clip_pool_dir.exists():
                raise FileNotFoundError(f"Clip pool directory not found: {clip_pool_dir}")
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"🎵 Starting optimized video generation...")
            
            # Step 1: Load and analyze audio
            self.logger.info("📊 Step 1/5: Analyzing audio...")
            audio_data = self.audio_loader.load(str(music_path))
            if audio_data is None:
                raise ValueError("Failed to load audio data")
            
            beats, beats_frames = self.beat_detector.detect(audio_data)
            if beats is None or len(beats) == 0:
                raise ValueError("No beats detected in audio")
            self.logger.info(f"   ✅ Detected {len(beats)} beats")
            
            # Step 2: Load and analyze clips
            self.logger.info("🎞️  Step 2/5: Analyzing clip pool...")
            clips = self.video_loader.load_directory(str(clip_pool_dir))
            if not clips:
                raise ValueError("No video clips found in directory")
            
            clip_features = self.video_analyzer.analyze_all(clips)
            if not clip_features:
                raise ValueError("Failed to analyze clips")
            self.logger.info(f"   ✅ Analyzed {len(clips)} clips")
            
            # Memory monitoring
            if self.gpu_accelerator:
                memory_info = self.gpu_accelerator.get_memory_info()
                self.logger.info(f"   GPU Memory: {memory_info['allocated_mb']:.0f}MB/{memory_info['total_mb']:.0f}MB")
            
            # Step 3: Generate cutting timeline
            self.logger.info("✂️  Step 3/5: Generating cutting timeline...")
            timeline = self.director.generate_timeline(
                beats=beats,
                clip_features=clip_features,
                audio_data=audio_data,
                metadata=metadata,
            )
            if timeline is None or not timeline.segments:
                raise ValueError("Failed to generate timeline")
            self.logger.info(f"   ✅ Generated timeline with {len(timeline.segments)} segments")
            
            # Step 4: Compose effects
            self.logger.info("✨ Step 4/5: Composing visual effects...")
            effect_chain = self.effect_composer.compose(
                timeline=timeline,
                clip_features=clip_features,
                beats=beats,
            )
            if effect_chain is None:
                raise ValueError("Failed to compose effects")
            self.logger.info(f"   ✅ Composed effect chain with {len(effect_chain.effects)} effects")
            
            # Step 5: Render final video
            self.logger.info("🎬 Step 5/5: Rendering final video...")
            output_path = self._render_video(
                timeline=timeline,
                effect_chain=effect_chain,
                audio_data=audio_data,
                output_path=str(output_path),
                clips=clips,
            )
            
            elapsed_time = time.time() - start_time
            self.logger.success(f"✅ Video generated successfully!")
            self.logger.success(f"   Output: {output_path}")
            self.logger.success(f"   Time: {elapsed_time:.1f}s")
            
            return output_path
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"❌ Pipeline failed after {elapsed_time:.1f}s: {str(e)}")
            if self.config.debug_mode:
                self.logger.exception("Full traceback:")
            raise
        finally:
            # Cleanup GPU memory
            if self.gpu_accelerator:
                self.gpu_accelerator.clear_cache()
