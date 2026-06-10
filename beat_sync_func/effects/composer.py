"""
Effect chain composition and management.
"""

from dataclasses import dataclass, field
from typing import List
import numpy as np
from loguru import logger
from beat_sync_func.core.config import Config


@dataclass
class Effect:
    """A single visual effect."""
    
    name: str
    type: str  # transition, temporal, spatial, color
    start_time: float
    duration: float
    parameters: dict = field(default_factory=dict)


@dataclass
class EffectChain:
    """Chain of effects to apply."""
    
    effects: List[Effect]
    total_effects: int


class EffectComposer:
    """Compose and manage visual effects."""
    
    def __init__(self, config: Config):
        """Initialize effect composer."""
        self.config = config
        np.random.seed(42)  # For reproducibility
    
    def compose(
        self,
        timeline,
        clip_features: list,
        beats: np.ndarray,
    ) -> EffectChain:
        """
        Compose effects for the timeline.
        
        Args:
            timeline: Timeline object with segments
            clip_features: List of clip features
            beats: Array of beat times
        
        Returns:
            EffectChain object
        
        Raises:
            ValueError: If effect composition fails
        """
        try:
            logger.info("Composing visual effects...")
            
            if not timeline.segments:
                raise ValueError("Timeline has no segments")
            
            effects = []
            
            # Add transition effects between segments
            if self.config.effects.enable_transitions and self.config.effects.transition_probability > 0:
                effects.extend(self._compose_transitions(timeline))
            
            # Add beat-synced effects
            effects.extend(self._compose_beat_effects(beats, timeline.total_duration))
            
            # Add spatial effects (zoom, pan)
            if self.config.effects.enable_zoom and self.config.effects.zoom_probability > 0:
                effects.extend(self._compose_spatial_effects(timeline))
            
            # Add temporal effects (time warps, speed changes)
            if self.config.effects.enable_time_warps and self.config.effects.time_warp_probability > 0:
                effects.extend(self._compose_temporal_effects(timeline))
            
            # Sort effects by start time
            effects.sort(key=lambda e: e.start_time)
            
            effect_chain = EffectChain(
                effects=effects,
                total_effects=len(effects),
            )
            
            logger.info(f"✅ Effects composed: {len(effects)} effects in chain")
            return effect_chain
            
        except Exception as e:
            logger.error(f"Effect composition failed: {e}")
            raise
    
    def _compose_transitions(self, timeline) -> List[Effect]:
        """Create transition effects between clips."""
        transitions = []
        
        for i, segment in enumerate(timeline.segments[:-1]):
            if np.random.random() > self.config.effects.transition_probability:
                continue
            
            transition = Effect(
                name=f"transition_{i}",
                type="transition",
                start_time=segment.start_time + segment.duration - self.config.cutter.transition_duration,
                duration=self.config.cutter.transition_duration,
                parameters={
                    'blend_mode': self.config.effects.blend_mode,
                    'intensity': self.config.effects.effect_intensity,
                },
            )
            transitions.append(transition)
        
        return transitions
    
    def _compose_beat_effects(self, beats: np.ndarray, duration: float) -> List[Effect]:
        """Create beat-synced effects."""
        beat_effects = []
        
        for i, beat_time in enumerate(beats):
            if beat_time >= duration:
                break
            
            effect = Effect(
                name=f"beat_pulse_{i}",
                type="color",
                start_time=beat_time,
                duration=0.1,
                parameters={
                    'type': 'pulse',
                    'intensity': self.config.effects.effect_intensity,
                },
            )
            beat_effects.append(effect)
        
        return beat_effects
    
    def _compose_spatial_effects(self, timeline) -> List[Effect]:
        """Create spatial effects (zoom, pan)."""
        spatial_effects = []
        
        for i, segment in enumerate(timeline.segments):
            if np.random.random() > self.config.effects.zoom_probability:
                continue
            
            zoom = Effect(
                name=f"zoom_{i}",
                type="spatial",
                start_time=segment.start_time,
                duration=segment.duration,
                parameters={
                    'zoom_direction': np.random.choice(['center_out', 'center_in', 'pan_left', 'pan_right']),
                    'intensity': np.random.uniform(1.0, 1.5 * self.config.effects.effect_intensity),
                },
            )
            spatial_effects.append(zoom)
        
        return spatial_effects
    
    def _compose_temporal_effects(self, timeline) -> List[Effect]:
        """Create temporal effects (time warps, speed changes)."""
        temporal_effects = []
        
        for i, segment in enumerate(timeline.segments):
            if np.random.random() > self.config.effects.time_warp_probability:
                continue
            
            # Apply time warp in the middle of the segment
            warp_start = segment.start_time + segment.duration * 0.5
            warp_duration = segment.duration * 0.3
            
            time_warp = Effect(
                name=f"time_warp_{i}",
                type="temporal",
                start_time=warp_start,
                duration=warp_duration,
                parameters={
                    'speed': np.random.uniform(0.5, 2.0 * self.config.effects.effect_intensity),
                },
            )
            temporal_effects.append(time_warp)
        
        return temporal_effects