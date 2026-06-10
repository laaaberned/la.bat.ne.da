"""
Updated core pipeline with rendering.
"""

import time
from pathlib import Path
from typing import Optional

from loguru import logger

from beat_sync_func.core.config import Config
from beat_sync_func.core.optimized_pipeline import OptimizedBeatSyncPipeline
from beat_sync_func.rendering.compositor import VideoCompositor


class RenderingBeatSyncPipeline(OptimizedBeatSyncPipeline):
    """Beat sync pipeline with rendering engine."""
    
    def __init__(self, config: Config, detect_hardware: bool = True):
        """Initialize pipeline with rendering."""
        super().__init__(config, detect_hardware)
        
        self.compositor = VideoCompositor(
            fps=config.video.fps,
            resolution=config.video.resolution,
            quality=config.video.quality,
        )
        logger.info("✅ Rendering engine initialized")
    
    def process(
        self,
        music_path: str,
        clip_pool_dir: str,
        output_path: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Process video with full rendering."""
        
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
            
            self.logger.info(f"🎬 BEAT SYNC RENDERER - Starting full pipeline")
            
            # Step 1: Load and analyze audio
            self.logger.info("① Audio Analysis")
            audio_data = self.audio_loader.load(str(music_path))
            if audio_data is None:
                raise ValueError("Failed to load audio data")
            
            beats, beats_frames = self.beat_detector.detect(audio_data)
            if beats is None or len(beats) == 0:
                raise ValueError("No beats detected in audio")
            self.logger.info(f"   ✅ {len(beats)} beats detected")
            
            # Step 2: Load and analyze clips
            self.logger.info("② Clip Analysis")
            clips = self.video_loader.load_directory(str(clip_pool_dir))
            if not clips:
                raise ValueError("No video clips found")
            
            clip_features = self.video_analyzer.analyze_all(clips)
            if not clip_features:
                raise ValueError("Failed to analyze clips")
            self.logger.info(f"   ✅ {len(clips)} clips analyzed")
            
            # Step 3: Generate timeline
            self.logger.info("③ Timeline Generation")
            timeline = self.director.generate_timeline(
                beats=beats,
                clip_features=clip_features,
                audio_data=audio_data,
                metadata=metadata,
            )
            if timeline is None or not timeline.segments:
                raise ValueError("Failed to generate timeline")
            self.logger.info(f"   ✅ {len(timeline.segments)} segments created")
            
            # Step 4: Compose effects
            self.logger.info("④ Effect Composition")
            effect_chain = self.effect_composer.compose(
                timeline=timeline,
                clip_features=clip_features,
                beats=beats,
            )
            if effect_chain is None:
                raise ValueError("Failed to compose effects")
            self.logger.info(f"   ✅ {len(effect_chain.effects)} effects composed")
            
            # Step 5: Render video
            self.logger.info("⑤ Video Rendering")
            
            # Get clip paths
            clip_paths = [clip['path'] for clip in clips]
            
            output_video = self.compositor.render_timeline(
                timeline=timeline,
                clip_paths=clip_paths,
                audio_path=str(music_path),
                output_path=str(output_path),
                effect_chain=effect_chain,
            )
            
            elapsed_time = time.time() - start_time
            
            self.logger.success(f"\n{'='*60}")
            self.logger.success(f"✅ VIDEO GENERATION COMPLETE!")
            self.logger.success(f"{'='*60}")
            self.logger.success(f"Output: {output_video}")
            self.logger.success(f"Duration: {elapsed_time:.1f} seconds")
            self.logger.success(f"Resolution: {self.config.video.resolution[0]}x{self.config.video.resolution[1]}")
            self.logger.success(f"FPS: {self.config.video.fps}")
            self.logger.success(f"{'='*60}\n")
            
            return output_video
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"\n❌ RENDERING FAILED after {elapsed_time:.1f}s: {str(e)}")
            if self.config.debug_mode:
                self.logger.exception("Full traceback:")
            raise
        finally:
            if self.gpu_accelerator:
                self.gpu_accelerator.clear_cache()
