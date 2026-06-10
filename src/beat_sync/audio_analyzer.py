"""Audio analysis for BPM and beat detection"""

import numpy as np
import librosa
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioAnalysisResult:
    """Result of audio analysis"""
    bpm: float
    beats: np.ndarray  # Beat times in seconds
    onset_frames: np.ndarray  # Onset frames
    onset_times: np.ndarray  # Onset times in seconds
    tempogram: np.ndarray
    spectral_centroid: np.ndarray
    spectral_flux: np.ndarray
    rms_energy: np.ndarray
    zero_crossing_rate: np.ndarray
    metadata: Dict[str, Any]


class AudioAnalyzer:
    """Analyze audio files for BPM, beats, and acoustic features"""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512, n_fft: int = 2048):
        """
        Initialize audio analyzer
        
        Args:
            sr: Sample rate (Hz)
            hop_length: Number of samples per frame
            n_fft: FFT window size
        """
        self.sr = sr
        self.hop_length = hop_length
        self.n_fft = n_fft
    
    def analyze(self, audio_path: str) -> AudioAnalysisResult:
        """Analyze audio file and extract features"""
        logger.info(f"Analyzing audio: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        logger.info(f"Audio loaded: {duration:.2f}s at {sr}Hz")
        
        # Compute STFT
        S = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
        S_db = librosa.power_to_db(np.abs(S)**2, ref=np.max)
        
        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        onset_frames = librosa.onset.onset_detect(onset_env=onset_env, sr=sr, hop_length=self.hop_length, backtrack=True)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
        
        # Estimate tempo and beats
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
        
        logger.info(f"Detected BPM: {tempo:.1f}")
        logger.info(f"Detected {len(beat_times)} beats")
        
        # Compute acoustic features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)[0]
        spectral_flux = np.sqrt(np.sum(np.diff(librosa.power_to_db(np.abs(S))**2, axis=1)**2, axis=0))
        rms_energy = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y, hop_length=self.hop_length)[0]
        
        # Compute tempogram
        tempogram = librosa.feature.tempogram(y=y, sr=sr, hop_length=self.hop_length)
        
        metadata = {
            "file": audio_path,
            "duration_seconds": float(duration),
            "sample_rate": sr,
            "num_samples": len(y),
            "num_beats": len(beat_times),
            "num_onsets": len(onset_times)
        }
        
        return AudioAnalysisResult(
            bpm=float(tempo),
            beats=beat_times,
            onset_frames=onset_frames,
            onset_times=onset_times,
            tempogram=tempogram,
            spectral_centroid=spectral_centroid,
            spectral_flux=spectral_flux,
            rms_energy=rms_energy,
            zero_crossing_rate=zero_crossing_rate,
            metadata=metadata
        )
