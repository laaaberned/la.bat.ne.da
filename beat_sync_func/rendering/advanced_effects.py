"""
Advanced effects rendering.
"""

import cv2
import numpy as np
from loguru import logger
from typing import Tuple


class AdvancedEffects:
    """Advanced visual effects rendering."""
    
    @staticmethod
    def apply_motion_blur(
        frame: np.ndarray,
        intensity: float = 0.5,
    ) -> np.ndarray:
        """Apply motion blur effect."""
        
        kernel_size = max(3, int(21 * intensity))
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Create motion blur kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        kernel = kernel / np.sum(kernel)
        
        return cv2.filter2D(frame, -1, kernel)
    
    @staticmethod
    def apply_glitch_effect(
        frame: np.ndarray,
        intensity: float = 0.3,
    ) -> np.ndarray:
        """Apply glitch/scan lines effect."""
        
        h, w = frame.shape[:2]
        
        # Create glitch
        num_glitches = max(1, int(h * intensity * 0.1))
        
        for _ in range(num_glitches):
            glitch_y = np.random.randint(0, h)
            glitch_height = max(1, int(h * intensity * 0.05))
            glitch_x = np.random.randint(-int(w * 0.1), int(w * 0.1))
            
            if glitch_y + glitch_height < h and glitch_x + w < w:
                if glitch_x >= 0:
                    frame[glitch_y:glitch_y + glitch_height, glitch_x:glitch_x + w] = \
                        frame[glitch_y:glitch_y + glitch_height, :w - glitch_x]
        
        return frame
    
    @staticmethod
    def apply_chromatic_aberration(
        frame: np.ndarray,
        intensity: float = 0.02,
    ) -> np.ndarray:
        """Apply chromatic aberration (color separation)."""
        
        h, w = frame.shape[:2]
        offset = max(1, int(w * intensity))
        
        # Split channels
        b, g, r = cv2.split(frame)
        
        # Shift red channel
        M = np.float32([[1, 0, offset], [0, 1, 0]])
        r = cv2.warpAffine(r, M, (w, h))
        
        # Shift blue channel opposite
        M = np.float32([[1, 0, -offset], [0, 1, 0]])
        b = cv2.warpAffine(b, M, (w, h))
        
        # Merge channels
        return cv2.merge([b, g, r])
    
    @staticmethod
    def apply_bloom_effect(
        frame: np.ndarray,
        intensity: float = 0.5,
        threshold: int = 200,
    ) -> np.ndarray:
        """Apply bloom/glow effect."""
        
        # Create bloom by blurring bright areas
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Apply Gaussian blur to mask
        bloom = cv2.GaussianBlur(frame, (51, 51), 0)
        bloom = bloom * (mask[:, :, np.newaxis] / 255.0) * intensity
        
        # Add bloom to original
        return cv2.addWeighted(frame, 1.0, bloom.astype(frame.dtype), 1.0, 0)
    
    @staticmethod
    def apply_film_grain(
        frame: np.ndarray,
        intensity: float = 0.3,
    ) -> np.ndarray:
        """Apply film grain effect."""
        
        h, w = frame.shape[:2]
        
        # Generate grain noise
        grain = np.random.normal(0, intensity * 255, (h, w, 3))
        
        # Add grain to frame
        return np.uint8(np.clip(frame.astype(np.float32) + grain, 0, 255))
    
    @staticmethod
    def apply_edge_enhance(
        frame: np.ndarray,
        intensity: float = 0.5,
    ) -> np.ndarray:
        """Apply edge enhancement."""
        
        # Compute Laplacian for edge detection
        laplacian = cv2.Laplacian(frame, cv2.CV_64F)
        
        # Enhance edges
        enhanced = frame.astype(np.float32) + laplacian * intensity
        
        return np.uint8(np.clip(enhanced, 0, 255))
    
    @staticmethod
    def apply_color_grade(
        frame: np.ndarray,
        lut: np.ndarray,
    ) -> np.ndarray:
        """Apply color grading using LUT (Look-Up Table)."""
        
        # Apply LUT to each channel
        b, g, r = cv2.split(frame)
        b = cv2.LUT(b, lut[:, 0])
        g = cv2.LUT(g, lut[:, 1])
        r = cv2.LUT(r, lut[:, 2])
        
        return cv2.merge([b, g, r])
    
    @staticmethod
    def apply_wave_distortion(
        frame: np.ndarray,
        intensity: float = 0.1,
        frequency: float = 0.05,
    ) -> np.ndarray:
        """Apply wave/ripple distortion effect."""
        
        h, w = frame.shape[:2]
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Create wave distortion
        wave_x = x + intensity * w * np.sin(2 * np.pi * frequency * y / h)
        wave_y = y + intensity * h * np.sin(2 * np.pi * frequency * x / w)
        
        # Clip to valid range
        wave_x = np.clip(wave_x, 0, w - 1).astype(np.float32)
        wave_y = np.clip(wave_y, 0, h - 1).astype(np.float32)
        
        # Remap frame
        return cv2.remap(frame, wave_x, wave_y, cv2.INTER_LINEAR)
    
    @staticmethod
    def apply_vhs_effect(
        frame: np.ndarray,
        intensity: float = 0.5,
    ) -> np.ndarray:
        """Apply VHS tape effect (combination of effects)."""
        
        # Apply scan lines
        h, w = frame.shape[:2]
        for i in range(0, h, 4):
            frame[i:i+2] = (frame[i:i+2].astype(np.float32) * 0.7).astype(np.uint8)
        
        # Add color shift
        frame = AdvancedEffects.apply_chromatic_aberration(frame, intensity * 0.05)
        
        # Add grain
        frame = AdvancedEffects.apply_film_grain(frame, intensity * 0.3)
        
        return frame
    
    @staticmethod
    def apply_kaleidoscope(
        frame: np.ndarray,
        segments: int = 6,
    ) -> np.ndarray:
        """Apply kaleidoscope effect."""
        
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Create output frame
        output = np.zeros_like(frame)
        
        # Sample from center triangular sections
        for seg in range(segments):
            angle = 2 * np.pi * seg / segments
            angle_next = 2 * np.pi * (seg + 1) / segments
            
            # Create mask for this segment (simplified)
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.ellipse(mask, (cx, cy), (cx, cy), 0, 
                       int(np.degrees(angle)), int(np.degrees(angle_next)), 255, -1)
            
            # Copy and rotate
            output[mask == 255] = frame[mask == 255]
        
        return output


class LUTGenerator:
    """Generate color grading Look-Up Tables (LUTs)."""
    
    @staticmethod
    def create_cool_lut() -> np.ndarray:
        """Create cool color grade LUT."""
        lut = np.zeros((256, 3), dtype=np.uint8)
        
        for i in range(256):
            lut[i, 0] = min(255, int(i * 1.2))  # Blue channel boost
            lut[i, 1] = int(i * 0.9)  # Green channel reduction
            lut[i, 2] = int(i * 0.8)  # Red channel reduction
        
        return lut
    
    @staticmethod
    def create_warm_lut() -> np.ndarray:
        """Create warm color grade LUT."""
        lut = np.zeros((256, 3), dtype=np.uint8)
        
        for i in range(256):
            lut[i, 0] = int(i * 0.8)  # Blue channel reduction
            lut[i, 1] = int(i * 0.95)  # Green channel slight reduction
            lut[i, 2] = min(255, int(i * 1.2))  # Red channel boost
        
        return lut
    
    @staticmethod
    def create_cinematic_lut() -> np.ndarray:
        """Create cinematic color grade LUT."""
        lut = np.zeros((256, 3), dtype=np.uint8)
        
        for i in range(256):
            # Slight cyan in shadows, slight orange in highlights
            lut[i, 0] = min(255, int(i * 1.1))  # Blue/cyan boost
            lut[i, 1] = int(i * 1.0)  # Green neutral
            lut[i, 2] = int(i * 0.95)  # Red slight reduction
        
        return lut
