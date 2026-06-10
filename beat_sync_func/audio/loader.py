"""
Audio loading and preprocessing.
"""

import librosa
import numpy as np
from loguru import logger
from beat_sync_func.core.config import Config


class AudioLoader:
    """Load and preprocess audio files."""
    
    def __init__(self, config: Config):
        """Initialize audio loader."""
        self.config = config
        self.sr = config.audio.sample_rate
    
    def load(self, audio_path: str) -> dict:
        """
        Load and preprocess audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary containing audio data and metadata
        """
        logger.info(f"Loading audio: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sr, mono=True)
        
        # Compute features
        S = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=self.config.audio.n_fft,
            hop_length=self.config.audio.hop_length,
            n_mels=self.config.audio.spectral_bins,
        )
        
        audio_data = {
            'waveform': y,
            'sample_rate': sr,
            'duration': len(y) / sr,
            'spectrogram': librosa.power_to_db(S, ref=np.max),
            'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
        }
        
        logger.info(f"✅ Audio loaded: {audio_data['duration']:.1f}s @ {sr}Hz")
        return audio_data