"""
Video rendering and compositing engine.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from loguru import logger
import tempfile
import os

from beat_sync_func.rendering.ffmpeg_wrapper import FFmpegRenderer


class VideoCompositor:
    """Compose and render video sequences with effects."""
    
    def __init__(
        self,
        fps: int = 30,
        resolution: Tuple[int, int] = (1920, 1080),
        quality: int = 23,
    ):
        """Initialize video compositor."""
        self.fps = fps
        self.resolution = resolution
        self.quality = quality
        self.ffmpeg = FFmpegRenderer()
        self.temp_dir = tempfile.mkdtemp(prefix='beat_sync_')
        logger.info(f"Compositor initialized: {resolution[0]}x{resolution[1]} @ {fps}fps")
    
    def render_timeline(
        self,
        timeline,
        clip_paths: List[str],
        audio_path: str,
        output_path: str,
        effect_chain=None,
    ) -> str:
        """
        Render complete timeline with effects.
        
        Args:
            timeline: Timeline object with segments
            clip_paths: List of clip video paths
            audio_path: Path to audio file
            output_path: Output video path
            effect_chain: Optional effect chain
        
        Returns:
            Path to rendered video
        """
        try:
            logger.info(f"🎬 Rendering timeline ({len(timeline.segments)} segments)...")
            
            # Step 1: Extract frames from clips
            logger.info("📽️  Step 1/5: Extracting clip frames...")
            clip_frames = self._extract_clip_frames(clip_paths, timeline)
            
            # Step 2: Compose frames with effects
            logger.info("✨ Step 2/5: Applying effects...")
            composed_frames = self._compose_frames_with_effects(
                clip_frames,
                timeline,
                effect_chain
            )
            
            # Step 3: Create video from frames
            logger.info("🎥 Step 3/5: Creating video from frames...")
            video_only_path = self._create_video_from_frames(composed_frames)
            
            # Step 4: Mix audio
            logger.info("🎵 Step 4/5: Mixing audio...")
            final_video = self._mix_audio_to_video(video_only_path, audio_path, output_path)
            
            # Step 5: Cleanup
            logger.info("🧹 Step 5/5: Cleaning up temporary files...")
            self._cleanup_temp_files()
            
            logger.info(f"✅ Rendering complete: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            self._cleanup_temp_files()
            raise
    
    def _extract_clip_frames(
        self,
        clip_paths: List[str],
        timeline,
    ) -> dict:
        """Extract frames from all clips used in timeline."""
        clip_frames = {}
        
        # Get unique clip indices used
        unique_clips = set(seg.clip_index for seg in timeline.segments)
        
        for clip_idx in sorted(unique_clips):
            if clip_idx >= len(clip_paths):
                logger.warning(f"Clip {clip_idx} not found")
                continue
            
            clip_path = clip_paths[clip_idx]
            logger.info(f"  Extracting frames from clip {clip_idx}: {Path(clip_path).name}")
            
            # Create temp directory for this clip
            clip_temp_dir = Path(self.temp_dir) / f'clip_{clip_idx}'
            clip_temp_dir.mkdir(exist_ok=True)
            
            frame_pattern = str(clip_temp_dir / 'frame_%04d.png')
            
            # Extract frames
            try:
                frames = self.ffmpeg.extract_frames(
                    clip_path,
                    frame_pattern,
                    fps=self.fps
                )
                clip_frames[clip_idx] = frames
                logger.info(f"    ✅ Extracted {len(frames)} frames")
            except Exception as e:
                logger.warning(f"    ❌ Failed to extract: {e}")
        
        return clip_frames
    
    def _compose_frames_with_effects(
        self,
        clip_frames: dict,
        timeline,
        effect_chain=None,
    ) -> List[str]:
        """Compose frames with effects."""
        
        # Create output directory for composed frames
        output_dir = Path(self.temp_dir) / 'composed'
        output_dir.mkdir(exist_ok=True)
        
        composed_frames = []
        frame_counter = 0
        
        logger.info(f"Composing {len(timeline.segments)} segments...")
        
        for seg_idx, segment in enumerate(timeline.segments):
            clip_idx = segment.clip_index
            
            if clip_idx not in clip_frames:
                logger.warning(f"Clip {clip_idx} frames not available")
                continue
            
            frames = clip_frames[clip_idx]
            
            # Calculate frame indices from segment
            start_frame = int(segment.clip_start * self.fps)
            num_frames = int(segment.duration * self.fps)
            num_frames = min(num_frames, len(frames) - start_frame)
            
            if num_frames <= 0:
                continue
            
            # Process frames
            for frame_offset in range(num_frames):
                frame_idx = start_frame + frame_offset
                
                if frame_idx >= len(frames):
                    break
                
                frame_path = frames[frame_idx]
                frame = cv2.imread(frame_path)
                
                if frame is None:
                    logger.warning(f"Failed to read frame: {frame_path}")
                    continue
                
                # Resize to target resolution
                frame = cv2.resize(frame, self.resolution)
                
                # Apply effects if available
                if effect_chain:
                    frame = self._apply_effects_to_frame(
                        frame,
                        segment,
                        frame_counter,
                        effect_chain
                    )
                
                # Save composed frame
                output_path = output_dir / f'frame_{frame_counter:06d}.png'
                cv2.imwrite(str(output_path), frame)
                composed_frames.append(str(output_path))
                
                frame_counter += 1
        
        logger.info(f"✅ Composed {len(composed_frames)} frames")
        return composed_frames
    
    def _apply_effects_to_frame(
        self,
        frame: np.ndarray,
        segment,
        frame_counter: int,
        effect_chain,
    ) -> np.ndarray:
        """Apply effects to a single frame."""
        
        # Get current time in video
        current_time = frame_counter / self.fps
        
        # Find applicable effects
        for effect in effect_chain.effects:
            if effect.start_time <= current_time <= effect.start_time + effect.duration:
                frame = self._apply_single_effect(frame, effect, current_time)
        
        return frame
    
    def _apply_single_effect(
        self,
        frame: np.ndarray,
        effect,
        current_time: float,
    ) -> np.ndarray:
        """Apply a single effect to frame."""
        
        if effect.type == 'transition':
            frame = self._apply_crossfade(frame, effect, current_time)
        elif effect.type == 'spatial':
            frame = self._apply_zoom(frame, effect, current_time)
        elif effect.type == 'temporal':
            frame = self._apply_time_warp(frame, effect, current_time)
        elif effect.type == 'color':
            frame = self._apply_color_effect(frame, effect, current_time)
        
        return frame
    
    def _apply_crossfade(
        self,
        frame: np.ndarray,
        effect,
        current_time: float,
    ) -> np.ndarray:
        """Apply crossfade transition."""
        
        # Calculate fade progress (0.0 to 1.0)
        effect_progress = (current_time - effect.start_time) / effect.duration
        effect_progress = np.clip(effect_progress, 0, 1)
        
        # Apply fade effect
        intensity = effect.parameters.get('intensity', 1.0)
        
        if effect_progress < 0.5:
            # Fade in
            alpha = effect_progress * 2 * intensity
            frame = cv2.addWeighted(frame, alpha, frame, 1 - alpha, 0)
        else:
            # Fade out
            alpha = (1 - effect_progress) * 2 * intensity
            frame = cv2.addWeighted(frame, alpha, frame, 1 - alpha, 0)
        
        return frame
    
    def _apply_zoom(
        self,
        frame: np.ndarray,
        effect,
        current_time: float,
    ) -> np.ndarray:
        """Apply zoom effect."""
        
        effect_progress = (current_time - effect.start_time) / effect.duration
        effect_progress = np.clip(effect_progress, 0, 1)
        
        intensity = effect.parameters.get('intensity', 1.2)
        zoom_direction = effect.parameters.get('zoom_direction', 'center_out')
        
        # Calculate zoom factor
        zoom_factor = 1.0 + (intensity - 1.0) * effect_progress
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Apply affine transformation
        matrix = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
        frame = cv2.warpAffine(frame, matrix, (w, h))
        
        return frame
    
    def _apply_time_warp(
        self,
        frame: np.ndarray,
        effect,
        current_time: float,
    ) -> np.ndarray:
        """Apply time warp (speed change) effect."""
        
        # Note: Time warp is mainly handled in frame extraction
        # This could add visual distortion effects
        
        intensity = effect.parameters.get('intensity', 1.0)
        
        if intensity > 1.0:
            # Fast motion effect: compress image
            h, w = frame.shape[:2]
            compress_factor = 1.0 / intensity
            new_w = max(1, int(w * compress_factor))
            new_h = max(1, int(h * compress_factor))
            frame = cv2.resize(frame, (new_w, new_h))
            frame = cv2.resize(frame, (w, h))  # Resize back
        
        return frame
    
    def _apply_color_effect(
        self,
        frame: np.ndarray,
        effect,
        current_time: float,
    ) -> np.ndarray:
        """Apply color effect."""
        
        effect_type = effect.parameters.get('type', 'pulse')
        intensity = effect.parameters.get('intensity', 1.0)
        
        if effect_type == 'pulse':
            # Brightness pulse
            progress = (current_time - effect.start_time) / effect.duration
            progress = np.clip(progress, 0, 1)
            
            # Pulse from 1.0 to 1.2
            brightness = 1.0 + 0.2 * np.sin(progress * np.pi)
            frame = cv2.convertScaleAbs(frame, alpha=brightness, beta=0)
        
        return frame
    
    def _create_video_from_frames(self, frame_paths: List[str]) -> str:
        """Create video from frame sequence."""
        
        output_path = Path(self.temp_dir) / 'video_no_audio.mp4'
        
        # Create frame pattern
        frame_dir = Path(frame_paths[0]).parent
        frame_pattern = str(frame_dir / 'frame_%06d.png')
        
        video_path = self.ffmpeg.create_video_from_frames(
            frame_pattern,
            fps=self.fps,
            output_path=str(output_path),
            quality=self.quality,
        )
        
        return video_path
    
    def _mix_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Mix audio with video."""
        
        return self.ffmpeg.mix_audio(video_path, audio_path, output_path, self.quality)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("✅ Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
