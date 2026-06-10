"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
from beat_sync_func.core.config import Config


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return Config(
        project_name="TEST_BEAT_SYNC",
        debug_mode=True,
    )


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing."""
    return {
        'input': tmp_path / 'input',
        'output': tmp_path / 'output',
        'temp': tmp_path / 'temp',
    }
