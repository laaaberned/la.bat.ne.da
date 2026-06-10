"""Generate beat-synced timelines from audio and video clips"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from src.visual_analysis.clip_analyzer import VisualMetadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TimelineClip:
    """A clip in the timeline"""
    clip_id: str
    file_path: str
    start_time_ms: float  # Timeline start time in milliseconds
    end_time_ms: float
    duration_ms: float
    transition_duration_ms: float
    start_frame: int
    end_frame: int
    metadata: dict


@dataclass
class Timeline:
    """Complete timeline of synced clips"""
    clips: List[TimelineClip]
    total_duration_ms: float
    fps: float
    audio_bpm: float
    beat_times_ms: List[float]
    metadata: dict


class TimelineGenerator:
    """Generate beat-synced timelines"""
    
    def __init__(
        self,
        transition_duration_ms: float = 500,
        min_clip_duration_ms: float = 500,
        max_clip_duration_ms: float = 8000
    ):
        """
        Initialize timeline generator
        
        Args:
            transition_duration_ms: Duration of transitions between clips
            min_clip_duration_ms: Minimum clip duration
            max_clip_duration_ms: Maximum clip duration
        """
        self.transition_duration_ms = transition_duration_ms
        self.min_clip_duration_ms = min_clip_duration_ms
        self.max_clip_duration_ms = max_clip_duration_ms
    
    def generate(
        self,
        selected_clips: List[Tuple[VisualMetadata, float]],
        beat_times: np.ndarray,
        bpm: float,
        fps: float = 30
    ) -> Timeline:
        """
        Generate timeline from selected clips
        
        Args:
            selected_clips: List of (VisualMetadata, sync_time_sec) tuples
            beat_times: Beat times in seconds
            bpm: Beats per minute
            fps: Frames per second
            
        Returns:
            Generated timeline
        """
        logger.info(f"Generating timeline with {len(selected_clips)} clips @ {bpm:.1f}BPM")
        
        timeline_clips = []
        current_time_ms = 0
        
        for i, (clip, sync_time) in enumerate(selected_clips):
            # Calculate clip duration
            clip_duration_ms = self._calculate_clip_duration(
                clip.duration,
                beat_times,
                sync_time
            )
            
            # Ensure within bounds
            clip_duration_ms = max(self.min_clip_duration_ms, min(clip_duration_ms, self.max_clip_duration_ms))
            
            # Calculate frame positions
            start_frame = int((current_time_ms / 1000.0) * fps)
            end_frame = int(((current_time_ms + clip_duration_ms) / 1000.0) * fps)
            
            timeline_clip = TimelineClip(
                clip_id=clip.clip_id,
                file_path=clip.file_path,
                start_time_ms=current_time_ms,
                end_time_ms=current_time_ms + clip_duration_ms,
                duration_ms=clip_duration_ms,
                transition_duration_ms=self.transition_duration_ms,
                start_frame=start_frame,
                end_frame=end_frame,
                metadata={
                    "shot_scale": clip.shot_scale,
                    "mood": clip.mood,
                    "composition_score": clip.composition_score,
                    "movement_intensity": clip.movement_intensity
                }
            )
            
            timeline_clips.append(timeline_clip)
            current_time_ms += clip_duration_ms + self.transition_duration_ms
            
            logger.debug(
                f"Clip {i+1}: {clip.clip_id} @ {current_time_ms/1000:.1f}s "
                f"(duration: {clip_duration_ms:.0f}ms)"
            )
        
        # Convert beat times to milliseconds
        beat_times_ms = (beat_times * 1000).tolist()
        
        total_duration_ms = current_time_ms - self.transition_duration_ms
        
        timeline = Timeline(
            clips=timeline_clips,
            total_duration_ms=total_duration_ms,
            fps=fps,
            audio_bpm=bpm,
            beat_times_ms=beat_times_ms,
            metadata={
                "num_clips": len(timeline_clips),
                "transition_duration_ms": self.transition_duration_ms,
                "total_duration_seconds": total_duration_ms / 1000.0
            }
        )
        
        logger.info(
            f"Timeline generated: {len(timeline_clips)} clips, "
            f"total duration {total_duration_ms/1000:.1f}s"
        )
        
        return timeline
    
    def _calculate_clip_duration(
        self,
        clip_duration: float,
        beat_times: np.ndarray,
        sync_time: float
    ) -> float:
        """Calculate duration for clip based on beat structure"""
        if len(beat_times) < 2:
            return min(clip_duration * 1000, self.max_clip_duration_ms)
        
        # Find nearest beat
        beat_idx = np.argmin(np.abs(beat_times - sync_time))
        
        if beat_idx < len(beat_times) - 1:
            beat_duration = beat_times[beat_idx + 1] - beat_times[beat_idx]
            # Use 2-4 beats as clip duration
            duration_beats = np.random.choice([2, 3, 4])
            calculated_duration = beat_duration * duration_beats * 1000
            return min(calculated_duration, self.max_clip_duration_ms)
        
        return min(clip_duration * 1000, self.max_clip_duration_ms)
