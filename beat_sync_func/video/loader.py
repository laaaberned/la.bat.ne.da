"""
Video loading and preprocessing.
"""

import cv2
from pathlib import Path
from loguru import logger
from beat_sync_func.core.config import Config


class VideoLoader:
    """Load and preprocess video files."""
    
    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    
    def __init__(self, config: Config):
        """Initialize video loader."""
        self.config = config
    
    def load(self, video_path: str) -> dict:
        """Load a single video file."""
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            logger.info(f"Loading video: {video_path.name}")
            
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Validate video properties
            if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
                raise ValueError(f"Invalid video properties: fps={fps}, frames={frame_count}, res={width}x{height}")
            
            duration = frame_count / fps
            cap.release()
            
            video_data = {
                'path': str(video_path),
                'fps': fps,
                'frame_count': frame_count,
                'resolution': (width, height),
                'duration': duration,
            }
            
            logger.info(f"✅ Video loaded: {duration:.1f}s @ {fps:.1f}fps ({width}x{height})")
            return video_data
            
        except Exception as e:
            logger.error(f"Failed to load video {video_path}: {e}")
            raise
    
    def load_directory(self, directory: str) -> list:
        """Load all video files from a directory."""
        video_dir = Path(directory)
        
        if not video_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not video_dir.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        logger.info(f"Loading clips from: {video_dir.name}")
        
        clips = []
        video_files = sorted([
            f for f in video_dir.iterdir() 
            if f.suffix.lower() in self.SUPPORTED_FORMATS
        ])
        
        if not video_files:
            logger.warning(f"No video files found in {directory}")
            return clips
        
        for video_file in video_files:
            try:
                clip = self.load(str(video_file))
                clips.append(clip)
            except Exception as e:
                logger.warning(f"Skipped {video_file.name}: {e}")
        
        logger.info(f"✅ Loaded {len(clips)}/{len(video_files)} clips")
        return clips