"""
Director engine for intelligent cutting decisions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from loguru import logger
from beat_sync_func.core.config import Config


@dataclass
class TimelineSegment:
    """A segment in the timeline."""
    
    clip_index: int
    start_time: float
    duration: float
    clip_start: float = 0.0  # Start position in source clip
    effect_type: str = "crossfade"
    energy_match: float = 1.0  # Energy match score


@dataclass
class Timeline:
    """Complete timeline for the video."""
    
    segments: List[TimelineSegment]
    total_duration: float
    beat_alignment: float
    metadata: dict = field(default_factory=dict)


class Director:
    """Intelligent cutting and timeline generation."""
    
    def __init__(self, config: Config):
        """Initialize director."""
        self.config = config
    
    def generate_timeline(
        self,
        beats: np.ndarray,
        clip_features: list,
        audio_data: dict,
        metadata: Optional[dict] = None,
    ) -> Timeline:
        """
        Generate an intelligent timeline based on beats and clip features.
        
        Args:
            beats: Array of beat times (in seconds)
            clip_features: List of clip feature dictionaries
            audio_data: Audio analysis data
            metadata: Optional metadata about the song
        
        Returns:
            Timeline object with segments
        
        Raises:
            ValueError: If timeline generation fails
        """
        try:
            logger.info("Generating intelligent cutting timeline...")
            
            if not clip_features:
                raise ValueError("No clips available for timeline generation")
            if not beats or len(beats) < 2:
                raise ValueError("Need at least 2 beats for timeline")
            
            segments = []
            current_time = 0.0
            music_duration = audio_data['duration']
            beat_idx = 0
            
            # Get average motion from all clips
            avg_motion = np.mean([c.get('motion_score', 0.5) for c in clip_features])
            
            # Generate segments based on beats
            while current_time < music_duration and beat_idx < len(beats) - 1:
                beat_duration = beats[beat_idx + 1] - beats[beat_idx]
                
                # Select clip intelligently
                clip_idx = self._select_clip(beat_idx, clip_features, avg_motion)
                clip = clip_features[clip_idx]
                
                # Calculate segment duration
                segment_duration = min(
                    beat_duration * np.random.uniform(0.9, 1.2),
                    clip['duration'] * 0.8,
                    self.config.cutter.max_cut_duration,
                )
                segment_duration = max(segment_duration, self.config.cutter.min_cut_duration)
                
                # Calculate energy match
                energy_match = self._calculate_energy_match(
                    beats[beat_idx],
                    clip['energy_level'],
                    audio_data
                )
                
                segment = TimelineSegment(
                    clip_index=clip_idx,
                    start_time=current_time,
                    duration=segment_duration,
                    clip_start=np.random.uniform(0, max(0, clip['duration'] - segment_duration)),
                    effect_type="crossfade",
                    energy_match=energy_match,
                )
                segments.append(segment)
                
                current_time += segment_duration - self.config.cutter.transition_duration
                beat_idx += 1
            
            total_duration = current_time
            beat_alignment = self._calculate_beat_alignment(beats, segments, music_duration)
            
            timeline = Timeline(
                segments=segments,
                total_duration=total_duration,
                beat_alignment=beat_alignment,
                metadata=metadata or {},
            )
            
            logger.info(f"✅ Timeline generated: {len(segments)} segments, {beat_alignment:.1%} beat alignment")
            return timeline
            
        except Exception as e:
            logger.error(f"Timeline generation failed: {e}")
            raise
    
    def _select_clip(
        self,
        beat_idx: int,
        clip_features: list,
        avg_motion: float,
    ) -> int:
        """Select a clip based on current beat and features."""
        # Simple round-robin selection
        return beat_idx % len(clip_features)
    
    def _calculate_energy_match(self, beat_time: float, clip_energy: str, audio_data: dict) -> float:
        """Calculate how well clip energy matches audio energy at beat time."""
        # Placeholder: return 1.0 for perfect match
        return 1.0
    
    def _calculate_beat_alignment(self, beats: np.ndarray, segments: list, duration: float) -> float:
        """Calculate how well segments align with beats."""
        if not beats or not segments:
            return 0.0
        
        alignment_score = 0.0
        for segment in segments:
            # Find closest beat
            closest_beat = min(beats, key=lambda b: abs(b - segment.start_time))
            distance = abs(closest_beat - segment.start_time)
            segment_alignment = max(0, 1.0 - (distance / 0.5))  # 0.5s tolerance
            alignment_score += segment_alignment
        
        return alignment_score / len(segments) if segments else 0.0