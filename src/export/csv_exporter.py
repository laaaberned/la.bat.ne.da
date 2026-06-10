"""Export timeline and metadata to CSV format"""

import csv
from pathlib import Path
from typing import List, Dict, Any
from src.timeline_generator.generator import Timeline
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVExporter:
    """Export data to CSV format"""
    
    def __init__(self, delimiter: str = ","):
        self.delimiter = delimiter
    
    def export_timeline(self, timeline: Timeline, output_path: str) -> None:
        """Export timeline to CSV file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare rows
        rows = []
        for i, clip in enumerate(timeline.clips):
            row = {
                "clip_number": i + 1,
                "clip_id": clip.clip_id,
                "file_path": clip.file_path,
                "start_time_ms": clip.start_time_ms,
                "start_time_sec": clip.start_time_ms / 1000.0,
                "end_time_ms": clip.end_time_ms,
                "end_time_sec": clip.end_time_ms / 1000.0,
                "duration_ms": clip.duration_ms,
                "duration_sec": clip.duration_ms / 1000.0,
                "transition_duration_ms": clip.transition_duration_ms,
                "start_frame": clip.start_frame,
                "end_frame": clip.end_frame,
                "shot_scale": clip.metadata.get("shot_scale", ""),
                "mood": clip.metadata.get("mood", ""),
                "composition_score": clip.metadata.get("composition_score", ""),
                "movement_intensity": clip.metadata.get("movement_intensity", "")
            }
            rows.append(row)
        
        # Write to CSV
        if rows:
            fieldnames = rows[0].keys()
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                writer.writerows(rows)
        
        logger.info(f"Exported timeline to CSV: {output_path}")
    
    def export_clip_analysis(self, clip_analyses: List[Dict[str, Any]], output_path: str) -> None:
        """Export clip analysis results to CSV"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if clip_analyses:
            fieldnames = clip_analyses[0].keys()
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                writer.writerows(clip_analyses)
        
        logger.info(f"Exported clip analysis to CSV: {output_path}")
