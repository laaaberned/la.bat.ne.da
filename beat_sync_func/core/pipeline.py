"""
Main pipeline orchestration for BEAT SYNC FUNC.
"""

import time
from pathlib import Path
from typing import Optional

from loguru import logger

from beat_sync_func.core.config import Config
from beat_sync_func.audio.loader import AudioLoader
from beat_sync_func.audio.beat_detector import BeatDetector
from beat_sync_func.video.loader import VideoLoader
from beat_sync_func.video.analyzer import VideoAnalyzer
from beat_sync_func.cutter.director import Director
from beat_sync_func.effects.composer import EffectComposer


class BeatSyncPipeline:
    """Main pipeline for generating beat-synced music videos."""
    
    def __init__(self, config: Config):
        """Initialize the pipeline with configuration."""
        self.config = config
        self.logger = logger
        
        # Initialize components
        self.audio_loader = AudioLoader(config)
        self.beat_detector = BeatDetector(config)
        self.video_loader = VideoLoader(config)
        self.video_analyzer = VideoAnalyzer(config)
        self.director = Director(config)
        self.effect_composer = EffectComposer(config)
        
        self.logger.info("🎬 BEAT SYNC FUNC Pipeline initialized")
    
    def process(
        self,
        music_path: str,
        clip_pool_dir: str,
        output_path: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Process a complete music video generation pipeline.
        
        Args:
            music_path: Path to the music file (MP3, WAV, etc.)
            clip_pool_dir: Directory containing video clips
            output_path: Path for the output video
            metadata: Optional metadata (artist, title, tags, etc.)
        
        Returns:
            Path to the generated video file
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🎵 Starting video generation process...")
            self.logger.info(f"   Music: {music_path}")
            self.logger.info(f"   Clips: {clip_pool_dir}")
            
            # Step 1: Load and analyze audio
            self.logger.info("📊 Step 1/5: Analyzing audio...")
            audio_data = self.audio_loader.load(music_path)
            beats, beats_frames = self.beat_detector.detect(audio_data)
            self.logger.info(f"   ✅ Detected {len(beats)} beats")
            
            # Step 2: Load and analyze clips
            self.logger.info("🎞️  Step 2/5: Analyzing clip pool...")
            clips = self.video_loader.load_directory(clip_pool_dir)
            clip_features = self.video_analyzer.analyze_all(clips)
            self.logger.info(f"   ✅ Analyzed {len(clips)} clips")
            
            # Step 3: Generate cutting timeline
            self.logger.info("✂️  Step 3/5: Generating cutting timeline...")
            timeline = self.director.generate_timeline(
                beats=beats,
                clip_features=clip_features,
                audio_data=audio_data,
                metadata=metadata,
            )
            self.logger.info(f"   ✅ Generated timeline with {len(timeline.segments)} segments")
            
            # Step 4: Compose effects
            self.logger.info("✨ Step 4/5: Composing visual effects...")
            effect_chain = self.effect_composer.compose(
                timeline=timeline,
                clip_features=clip_features,
                beats=beats,
            )
            self.logger.info(f"   ✅ Composed effect chain with {len(effect_chain.effects)} effects")
            
            # Step 5: Render final video
            self.logger.info("🎬 Step 5/5: Rendering final video...")
            output_path = self._render_video(
                timeline=timeline,
                effect_chain=effect_chain,
                audio_data=audio_data,
                output_path=output_path,
            )
            
            elapsed_time = time.time() - start_time
            self.logger.success(f"✅ Video generated successfully!")
            self.logger.success(f"   Output: {output_path}")
            self.logger.success(f"   Time: {elapsed_time:.1f}s")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {str(e)}")
            raise
    
    def _render_video(
        self,
        timeline,
        effect_chain,
        audio_data,
        output_path: str,
    ) -> str:
        """Render the final video with effects and audio."""
        # Placeholder for actual rendering logic
        # Will be implemented in rendering module
        self.logger.info(f"   Placeholder: Rendering to {output_path}")
        return output_path