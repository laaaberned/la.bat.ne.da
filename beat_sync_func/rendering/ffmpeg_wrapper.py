"""
FFmpeg wrapper and video rendering engine.
"""

import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger
import json


class FFmpegRenderer:
    """Render videos using FFmpeg."""
    
    # FFmpeg binary locations
    FFMPEG_BIN = 'ffmpeg'
    FFPROBE_BIN = 'ffprobe'
    
    def __init__(self, timeout: int = 3600):
        """Initialize FFmpeg renderer."""
        self.timeout = timeout
        self._check_ffmpeg_installed()
    
    def _check_ffmpeg_installed(self):
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(
                [self.FFMPEG_BIN, '-version'],
                capture_output=True,
                timeout=5,
                check=True
            )
            logger.info("✅ FFmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ FFmpeg not installed")
            raise RuntimeError("FFmpeg is required. Install with: apt-get install ffmpeg")
    
    def get_video_info(self, video_path: str) -> dict:
        """Get video information using ffprobe."""
        try:
            result = subprocess.run(
                [
                    self.FFPROBE_BIN,
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'stream=width,height,r_frame_rate,duration',
                    '-of', 'json',
                    video_path
                ],
                capture_output=True,
                timeout=10,
                check=True
            )
            
            data = json.loads(result.stdout)
            stream = data['streams'][0]
            
            width = stream.get('width', 0)
            height = stream.get('height', 0)
            fps_str = stream.get('r_frame_rate', '30/1')
            
            # Parse fps (format: "30/1" or "24000/1001")
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = num / den
            else:
                fps = float(fps_str)
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
            }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise
    
    def extract_frames(
        self,
        video_path: str,
        output_pattern: str,
        fps: Optional[float] = None,
        start_time: float = 0,
        duration: Optional[float] = None,
    ) -> List[str]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to input video
            output_pattern: Output pattern (e.g., 'frame_%04d.png')
            fps: Target FPS (optional)
            start_time: Start time in seconds
            duration: Duration in seconds (optional)
        
        Returns:
            List of extracted frame paths
        """
        try:
            logger.info(f"Extracting frames from {Path(video_path).name}")
            
            cmd = [self.FFMPEG_BIN, '-i', video_path]
            
            if start_time > 0:
                cmd.extend(['-ss', str(start_time)])
            
            if duration:
                cmd.extend(['-t', str(duration)])
            
            if fps:
                cmd.extend(['-vf', f'fps={fps}'])
            
            cmd.extend(['-y', output_pattern])  # -y = overwrite
            
            subprocess.run(cmd, timeout=self.timeout, check=True, capture_output=True)
            
            logger.info("✅ Frames extracted")
            
            # Count extracted frames
            output_dir = Path(output_pattern).parent
            output_name = Path(output_pattern).name
            frame_pattern = output_name.replace('%04d', '*')
            
            frames = sorted(output_dir.glob(frame_pattern))
            return [str(f) for f in frames]
            
        except subprocess.TimeoutExpired:
            logger.error("Frame extraction timeout")
            raise
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            raise
    
    def concatenate_videos(
        self,
        video_list: List[str],
        output_path: str,
        fps: int = 30,
        quality: int = 23,
    ) -> str:
        """
        Concatenate multiple video files.
        
        Args:
            video_list: List of video paths
            output_path: Output video path
            fps: Output FPS
            quality: CRF quality (0-51, lower = better)
        
        Returns:
            Path to output video
        """
        try:
            logger.info(f"Concatenating {len(video_list)} videos...")
            
            # Create concat demuxer file
            concat_file = Path(output_path).parent / 'concat.txt'
            with open(concat_file, 'w') as f:
                for video in video_list:
                    f.write(f"file '{Path(video).absolute()}'\n")
            
            cmd = [
                self.FFMPEG_BIN,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',  # Copy codec (fast)
                '-y', output_path
            ]
            
            subprocess.run(cmd, timeout=self.timeout, check=True, capture_output=True)
            
            concat_file.unlink()  # Clean up concat file
            logger.info(f"✅ Videos concatenated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Concatenation failed: {e}")
            raise
    
    def mix_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        quality: int = 23,
    ) -> str:
        """
        Mix audio with video.
        
        Args:
            video_path: Path to input video (video only)
            audio_path: Path to audio file
            output_path: Path to output video
            quality: CRF quality
        
        Returns:
            Path to output video
        """
        try:
            logger.info("Mixing audio with video...")
            
            cmd = [
                self.FFMPEG_BIN,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream
                '-c:a', 'aac',  # Encode audio
                '-b:a', '192k',
                '-shortest',  # Use shortest stream
                '-y', output_path
            ]
            
            subprocess.run(cmd, timeout=self.timeout, check=True, capture_output=True)
            logger.info(f"✅ Audio mixed: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio mixing failed: {e}")
            raise
    
    def create_video_from_frames(
        self,
        frame_pattern: str,
        fps: int = 30,
        output_path: str = 'output.mp4',
        quality: int = 23,
        pix_fmt: str = 'yuv420p',
    ) -> str:
        """
        Create video from image sequence.
        
        Args:
            frame_pattern: Pattern of frames (e.g., 'frame_%04d.png')
            fps: Frames per second
            output_path: Output video path
            quality: CRF quality (0-51)
            pix_fmt: Pixel format (yuv420p for compatibility)
        
        Returns:
            Path to output video
        """
        try:
            logger.info(f"Creating video from frames at {fps}fps...")
            
            cmd = [
                self.FFMPEG_BIN,
                '-framerate', str(fps),
                '-i', frame_pattern,
                '-c:v', 'libx264',
                '-pix_fmt', pix_fmt,
                '-crf', str(quality),
                '-preset', 'medium',  # medium balance between speed and quality
                '-y', output_path
            ]
            
            subprocess.run(cmd, timeout=self.timeout, check=True, capture_output=True)
            logger.info(f"✅ Video created: {output_path}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("Video creation timeout")
            raise
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            raise
    
    def apply_filter(
        self,
        input_path: str,
        filter_str: str,
        output_path: str,
    ) -> str:
        """
        Apply FFmpeg filter to video.
        
        Args:
            input_path: Input video
            filter_str: FFmpeg filter string (e.g., 'scale=1920:1080')
            output_path: Output video
        
        Returns:
            Path to output video
        """
        try:
            logger.info(f"Applying filter: {filter_str}")
            
            cmd = [
                self.FFMPEG_BIN,
                '-i', input_path,
                '-vf', filter_str,
                '-y', output_path
            ]
            
            subprocess.run(cmd, timeout=self.timeout, check=True, capture_output=True)
            logger.info(f"✅ Filter applied: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            raise
    
    def scale_video(
        self,
        input_path: str,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        """
        Scale video to specific resolution.
        
        Args:
            input_path: Input video
            width: Target width
            height: Target height
            output_path: Output video
        
        Returns:
            Path to output video
        """
        filter_str = f'scale={width}:{height}'
        return self.apply_filter(input_path, filter_str, output_path)
    
    def rotate_video(
        self,
        input_path: str,
        angle: float,  # 0, 90, 180, 270
        output_path: str,
    ) -> str:
        """
        Rotate video.
        
        Args:
            input_path: Input video
            angle: Rotation angle (0, 90, 180, 270)
            output_path: Output video
        
        Returns:
            Path to output video
        """
        # FFmpeg transpose filter: 0=90ccw, 1=90cw, 2=90ccw+flip, 3=90cw+flip
        transpose_map = {90: 1, 180: 1, 270: 2}
        
        if angle not in transpose_map:
            logger.warning(f"Unsupported angle: {angle}")
            return input_path
        
        transpose = transpose_map[angle]
        filter_str = f'transpose={transpose}'
        
        return self.apply_filter(input_path, filter_str, output_path)
    
    def crop_video(
        self,
        input_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        """
        Crop video.
        
        Args:
            input_path: Input video
            x, y: Top-left corner
            width, height: Crop dimensions
            output_path: Output video
        
        Returns:
            Path to output video
        """
        filter_str = f'crop={width}:{height}:{x}:{y}'
        return self.apply_filter(input_path, filter_str, output_path)
