"""
Audio loading and preprocessing.
"""

import librosa
import numpy as np
from pathlib import Path
from loguru import logger
from beat_sync_func.core.config import Config


class AudioLoader:
    """Load and preprocess audio files."""
    
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    
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
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported or loading fails
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
        
        try:
            logger.info(f"Loading audio: {audio_path}")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr, mono=True)
            
            if y is None or len(y) == 0:
                raise ValueError("Failed to load audio data")
            
            duration = len(y) / sr
            logger.info(f"   Loaded {duration:.1f}s of audio")
            
            # Compute features
            logger.info(f"   Computing spectral features...")
            S = librosa.feature.melspectrogram(
                y=y,
                sr=sr,
                n_fft=self.config.audio.n_fft,
                hop_length=self.config.audio.hop_length,
                n_mels=self.config.audio.spectral_bins,
            )
            
            # Normalize power to dB scale safely
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Compute MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Compute chroma
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            audio_data = {
                'path': str(audio_path),
                'waveform': y,
                'sample_rate': sr,
                'duration': duration,
                'spectrogram': S_db,
                'mfcc': mfcc,
                'chroma': chroma,
                'energy': librosa.feature.rms(y=y)[0],
            }
            
            logger.info(f"✅ Audio loaded: {duration:.1f}s @ {sr}Hz")
            return audio_data
            
        except librosa.util.exceptions.ParameterError as e:
            logger.error(f"Librosa parameter error: {e}")
            raise ValueError(f"Invalid audio parameters: {e}")
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            raise