"""Beat detection and synchronization"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BeatSyncPoint:
    """A point where clip should sync to beat"""
    beat_index: int
    beat_time: float
    clip_id: str
    start_frame: int
    duration_frames: int


class BeatDetector:
    """Detect and match beats for clip synchronization"""
    
    def __init__(self):
        pass
    
    def find_sync_points(
        self,
        beats: np.ndarray,
        bpm: float,
        clip_count: int,
        allow_beat_division: bool = True
    ) -> np.ndarray:
        """
        Find beat synchronization points for clips
        
        Args:
            beats: Beat times in seconds
            bpm: Beats per minute
            clip_count: Number of clips to sync
            allow_beat_division: Allow syncing to half-beats, quarter-beats
            
        Returns:
            Array of sync points (times in seconds)
        """
        if allow_beat_division:
            # Create sub-beat positions (half-beats and quarter-beats)
            sync_points = []
            for i in range(len(beats) - 1):
                beat_duration = beats[i + 1] - beats[i]
                sync_points.append(beats[i])
                sync_points.append(beats[i] + beat_duration * 0.5)
                sync_points.append(beats[i] + beat_duration * 0.25)
                sync_points.append(beats[i] + beat_duration * 0.75)
            sync_points.append(beats[-1])
            sync_points = np.array(sorted(sync_points))
        else:
            sync_points = beats
        
        logger.info(f"Generated {len(sync_points)} beat synchronization points")
        return sync_points
    
    def get_beat_duration(self, bpm: float) -> float:
        """Get duration of one beat in seconds"""
        return 60.0 / bpm
    
    def align_to_nearest_beat(self, time: float, beats: np.ndarray) -> Tuple[float, int]:
        """
        Find nearest beat to given time
        
        Args:
            time: Time in seconds
            beats: Array of beat times
            
        Returns:
            Tuple of (aligned_time, beat_index)
        """
        beat_index = np.argmin(np.abs(beats - time))
        return beats[beat_index], beat_index
