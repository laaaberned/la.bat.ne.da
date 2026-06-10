"""
BEAT SYNC FUNC - AI-Powered Music Video Creator

Automatically generate cinematic music videos from a clip pool,
perfectly synced to the beat.
"""

__version__ = "0.1.0"
__author__ = "laaaberned"
__description__ = "AI-powered music video creator with beat synchronization"

from beat_sync_func.core.pipeline import BeatSyncPipeline
from beat_sync_func.core.config import Config

__all__ = [
    "BeatSyncPipeline",
    "Config",
]

# Logging setup
from loguru import logger

logger.enable("beat_sync_func")