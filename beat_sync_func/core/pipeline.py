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
        try:
            self.audio_loader = AudioLoader(config)
            self.beat_detector = BeatDetector(config)
            self.video_loader = VideoLoader(config)
            self.video_analyzer = VideoAnalyzer(config)
            self.director = Director(config)
            self.effect_composer = EffectComposer(config)
            
            self.logger.info("🎬 BEAT SYNC FUNC Pipeline initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize pipeline: {e}")
            raise
    
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
        
        Raises:
            FileNotFoundError: If input files/directories don't exist
            ValueError: If processing fails
        """
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
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"🎵 Starting video generation process...")
            self.logger.info(f"   Music: {music_path}")
            self.logger.info(f"   Clips: {clip_pool_dir}")
            
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
            
        except FileNotFoundError as e:
            self.logger.error(f"❌ File not found: {e}")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"❌ Pipeline failed after {elapsed_time:.1f}s: {str(e)}")
            if self.config.debug_mode:
                self.logger.exception("Full traceback:")
            raise
    
    def _render_video(
        self,
        timeline,
        effect_chain,
        audio_data,
        output_path: str,
        clips: list,
    ) -> str:
        """Render the final video with effects and audio."""
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"   Rendering {len(timeline.segments)} segments...")
            
            # This is a placeholder for actual rendering logic
            # In production, this would use FFmpeg to:
            # 1. Extract and process each clip segment
            # 2. Apply effects from effect_chain
            # 3. Mix audio and video
            # 4. Write output file
            
            if self.config.debug_mode:
                self.logger.debug(f"   Timeline total duration: {timeline.total_duration:.2f}s")
                self.logger.debug(f"   Audio duration: {audio_data['duration']:.2f}s")
                self.logger.debug(f"   Number of effects: {len(effect_chain.effects)}")
            
            # Create a dummy output file for testing
            Path(output_path).touch()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Rendering failed: {e}")
            raise