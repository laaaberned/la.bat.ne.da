"""Smart clip selection to avoid repetition and ensure creative flow"""

import numpy as np
from typing import List, Dict, Tuple
from src.visual_analysis.clip_analyzer import VisualMetadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ClipSelector:
    """Select and sequence clips for timeline with creative logic"""
    
    def __init__(
        self,
        max_consecutive_same_shot_scale: int = 2,
        max_consecutive_same_mood: int = 3,
        weights: Dict[str, float] = None
    ):
        """
        Initialize clip selector
        
        Args:
            max_consecutive_same_shot_scale: Max consecutive clips with same shot scale
            max_consecutive_same_mood: Max consecutive clips with same mood
            weights: Weighting for selection criteria
        """
        self.max_consecutive_same_shot_scale = max_consecutive_same_shot_scale
        self.max_consecutive_same_mood = max_consecutive_same_mood
        self.weights = weights or {
            "composition": 0.3,
            "movement": 0.25,
            "lighting": 0.25,
            "mood": 0.2
        }
    
    def select_clips(
        self,
        available_clips: List[VisualMetadata],
        num_clips_needed: int,
        sync_points: np.ndarray
    ) -> List[Tuple[VisualMetadata, float]]:
        """
        Select clips for timeline
        
        Args:
            available_clips: List of available clips with metadata
            num_clips_needed: Number of clips to select
            sync_points: Beat synchronization points (times in seconds)
            
        Returns:
            List of (clip, start_time) tuples
        """
        logger.info(f"Selecting {num_clips_needed} clips from {len(available_clips)} available")
        
        selected = []
        used_clip_ids = set()
        last_shot_scale = None
        last_mood = None
        consecutive_scale = 0
        consecutive_mood = 0
        
        for i in range(num_clips_needed):
            if i >= len(sync_points):
                break
            
            sync_point = sync_points[i]
            
            # Find suitable clip
            candidates = [
                clip for clip in available_clips
                if clip.clip_id not in used_clip_ids
            ]
            
            if not candidates:
                logger.warning(f"No more unused clips available at position {i}")
                break
            
            # Filter by repetition rules
            candidates = self._apply_repetition_filters(
                candidates,
                last_shot_scale,
                last_mood,
                consecutive_scale,
                consecutive_mood
            )
            
            if not candidates:
                # If all filtered out, reset and allow any
                candidates = [
                    clip for clip in available_clips
                    if clip.clip_id not in used_clip_ids
                ]
            
            # Score candidates
            scores = self._score_clips(candidates)
            best_idx = np.argmax(scores)
            best_clip = candidates[best_idx]
            
            selected.append((best_clip, float(sync_point)))
            used_clip_ids.add(best_clip.clip_id)
            
            # Update tracking
            if best_clip.shot_scale == last_shot_scale:
                consecutive_scale += 1
            else:
                consecutive_scale = 1
                last_shot_scale = best_clip.shot_scale
            
            if best_clip.mood == last_mood:
                consecutive_mood += 1
            else:
                consecutive_mood = 1
                last_mood = best_clip.mood
            
            logger.debug(
                f"Selected clip {best_clip.clip_id}: {best_clip.shot_scale} "
                f"({best_clip.mood}) @ {sync_point:.2f}s"
            )
        
        logger.info(f"Selected {len(selected)} clips for timeline")
        return selected
    
    def _apply_repetition_filters(
        self,
        candidates: List[VisualMetadata],
        last_shot_scale: str,
        last_mood: str,
        consecutive_scale: int,
        consecutive_mood: int
    ) -> List[VisualMetadata]:
        """Filter candidates to avoid repetition"""
        filtered = candidates.copy()
        
        # Avoid too many consecutive same shot scales
        if consecutive_scale >= self.max_consecutive_same_shot_scale and last_shot_scale:
            filtered = [c for c in filtered if c.shot_scale != last_shot_scale]
        
        # Avoid too many consecutive same moods
        if consecutive_mood >= self.max_consecutive_same_mood and last_mood:
            filtered = [c for c in filtered if c.mood != last_mood]
        
        return filtered if filtered else candidates
    
    def _score_clips(self, clips: List[VisualMetadata]) -> np.ndarray:
        """Score clips based on selection criteria"""
        scores = np.zeros(len(clips))
        
        for i, clip in enumerate(clips):
            # Normalize scores to 0-1 range
            composition_score = clip.composition_score
            movement_score = clip.movement_intensity
            lighting_score = clip.lighting_intensity
            mood_score = clip.mood_score
            
            # Weighted combination
            weighted_score = (
                self.weights["composition"] * composition_score +
                self.weights["movement"] * movement_score +
                self.weights["lighting"] * lighting_score +
                self.weights["mood"] * mood_score
            )
            
            scores[i] = weighted_score
        
        return scores
