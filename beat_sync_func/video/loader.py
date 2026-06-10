"""
Video loading and preprocessing.
"""

import cv2
from pathlib import Path
from loguru import logger
from beat_sync_func.core.config import Config


class VideoLoader:
    """Load and preprocess video files."""
    
    def __init__(self, config: Config):
        """Initialize video loader."""
        self.config = config
    
    def load(self, video_path: str) -> dict:
        """Load a single video file."""
        logger.info(f"Loading video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        video_data = {
            'path': video_path,
            'fps': fps,
            'frame_count': frame_count,
            'resolution': (width, height),
            'duration': duration,
        }
        
        logger.info(f"✅ Video loaded: {duration:.1f}s @ {fps}fps ({width}x{height})")
        return video_data
    
    def load_directory(self, directory: str) -> list:
        """Load all video files from a directory."""
        logger.info(f"Loading clips from: {directory}")
        
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
        video_dir = Path(directory)
        
        clips = []
        for video_file in video_dir.iterdir():
            if video_file.suffix.lower() in video_extensions:
                try:
                    clip = self.load(str(video_file))
                    clips.append(clip)
                except Exception as e:
                    logger.warning(f"Could not load {video_file}: {e}")
        
        logger.info(f"✅ Loaded {len(clips)} clips")
        return clips