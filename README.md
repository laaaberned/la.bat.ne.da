# ART.WE.ED.IT - AI Music Video Editor

**Professional AI-powered music video editing with automatic beat synchronization and intelligent clip selection.**

## Overview

ART.WE.ED.IT combines:
- **Beat Sync**: Automatically synchronize video clips to music BPM and rhythm
- **Visual Analysis**: AI-powered extraction of shot composition, camera movement, lighting, and mood
- **Smart Selection**: Intelligent clip selection logic to avoid repetition and ensure creative flow
- **Timeline Generation**: Automatic beat-synced timeline creation from music and video clips
- **Export**: Comprehensive metadata export in JSON/CSV formats for further editing

## Features

### Core Capabilities

1. **Audio Analysis**
   - BPM detection from audio files
   - Beat position identification
   - Lyric timing extraction
   - Audio feature analysis (energy, spectral characteristics)

2. **Visual Analysis**
   - Shot scale detection (wide, medium, close-up)
   - Camera movement analysis
   - Lighting & mood classification
   - Composition evaluation
   - Scene transitions detection

3. **Clip Management**
   - Metadata extraction for all video clips
   - Historical tracking of analyses (date, parameters, clip ID)
   - Clip library organization

4. **Smart Timeline Generation**
   - Beat-synced clip sequencing
   - Repetition avoidance with creative logic
   - Thematic coherence maintenance
   - Shot composition flow optimization

5. **Export Functionality**
   - JSON export: Detailed metadata with all analysis parameters
   - CSV export: Tabular format for spreadsheet review
   - Timeline export: Editable project format
   - Analysis history: Review and re-run with different contexts

## Project Structure

```
la.bat.ne.da/
├── src/
│   ├── beat_sync/              # BPM detection and beat alignment
│   │   ├── __init__.py
│   │   ├── audio_analyzer.py   # Audio processing and BPM extraction
│   │   └── beat_detector.py    # Beat position detection
│   ├── visual_analysis/        # AI-powered visual metadata extraction
│   │   ├── __init__.py
│   │   ├── clip_analyzer.py    # Main visual analysis orchestrator
│   │   ├── composition.py      # Shot scale and composition analysis
│   │   ├── camera_movement.py  # Motion and camera tracking
│   │   └── lighting_mood.py    # Lighting and mood classification
│   ├── clip_selector/          # Smart clip selection engine
│   │   ├── __init__.py
│   │   ├── selector.py         # Main selection logic
│   │   ├── repetition_avoider.py
│   │   └── thematic_matcher.py # Match clips to music progression
│   ├── timeline_generator/     # Beat-synced timeline creation
│   │   ├── __init__.py
│   │   └── generator.py        # Timeline orchestration
│   ├── export/                 # Export functionality
│   │   ├── __init__.py
│   │   ├── json_exporter.py
│   │   └── csv_exporter.py
│   ├── core/                   # Main orchestration
│   │   ├── __init__.py
│   │   ├── project.py          # Project management
│   │   ├── database.py         # Analysis history tracking
│   │   └── pipeline.py         # Main processing pipeline
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── logger.py           # Logging utilities
├── models/                     # Pre-trained ML models
│   └── .gitkeep
├── data/
│   ├── clips/                  # Input video clips
│   │   └── .gitkeep
│   ├── audio/                  # Input audio files (MP3s)
│   │   └── .gitkeep
│   └── exports/                # Generated exports
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_audio_analyzer.py
│   ├── test_visual_analysis.py
│   └── test_timeline_generator.py
├── config.yaml                 # Project configuration
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md
```

## Installation

### Requirements
- Python 3.9+
- FFmpeg
- CUDA (optional, for GPU acceleration)

### Setup

```bash
# Clone repository
git clone https://github.com/laaaberned/la.bat.ne.da.git
cd la.bat.ne.da

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg
```

## Quick Start

```python
from src.core.pipeline import MusicVideoEditorPipeline

# Initialize pipeline
pipeline = MusicVideoEditorPipeline(config_path='config.yaml')

# Process music video
result = pipeline.process(
    audio_path='data/audio/song.mp3',
    clips_dir='data/clips/',
    output_dir='data/exports/'
)

# Export results
result.export_json('data/exports/timeline.json')
result.export_csv('data/exports/metadata.csv')
```

## Workflow

1. **Audio Analysis**: Extract BPM, beats, and lyrics timing from music file
2. **Visual Analysis**: Analyze all available video clips for metadata (composition, movement, lighting)
3. **Clip Selection**: Select clips for timeline based on creative logic and mood matching
4. **Timeline Generation**: Create beat-synced sequence with smooth transitions
5. **Export**: Generate JSON, CSV, and editable timeline formats
6. **Review**: Check analysis history and re-run with different parameters if needed

## Configuration

Edit `config.yaml` to customize:
- Audio analysis parameters
- Visual analysis model settings
- Timeline generation rules
- Export formats

## References

- **CutClaw**: https://github.com/GVCLab/CutClaw - Advanced video cutting techniques
- **BeatSync-Engine**: https://github.com/Merserk/BeatSync-Engine - Beat synchronization engine

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please open issues and pull requests.

---

**ART.WE.ED.IT** - Where AI meets creativity in music video production.
