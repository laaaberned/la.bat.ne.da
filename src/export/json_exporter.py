"""Export timeline and metadata to JSON format"""

import json
from pathlib import Path
from typing import Any, Dict
from src.timeline_generator.generator import Timeline
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JSONExporter:
    """Export data to JSON format"""
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def export_timeline(self, timeline: Timeline, output_path: str) -> None:
        """Export timeline to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert timeline to dict
        timeline_dict = {
            "metadata": {
                "total_duration_ms": timeline.total_duration_ms,
                "total_duration_seconds": timeline.total_duration_ms / 1000.0,
                "fps": timeline.fps,
                "audio_bpm": timeline.audio_bpm,
                "num_clips": len(timeline.clips),
                **timeline.metadata
            },
            "clips": [
                {
                    "clip_id": clip.clip_id,
                    "file_path": clip.file_path,
                    "start_time_ms": clip.start_time_ms,
                    "end_time_ms": clip.end_time_ms,
                    "duration_ms": clip.duration_ms,
                    "transition_duration_ms": clip.transition_duration_ms,
                    "start_frame": clip.start_frame,
                    "end_frame": clip.end_frame,
                    "metadata": clip.metadata
                }
                for clip in timeline.clips
            ],
            "beat_times_ms": timeline.beat_times_ms
        }
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(timeline_dict, f, indent=self.indent)
        
        logger.info(f"Exported timeline to JSON: {output_path}")
    
    def export_metadata(
        self,
        data: Dict[str, Any],
        output_path: str
    ) -> None:
        """Export metadata dictionary to JSON"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=self.indent)
        
        logger.info(f"Exported metadata to JSON: {output_path}")
