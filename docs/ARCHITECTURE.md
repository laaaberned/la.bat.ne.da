# BEAT SYNC FUNC - Architecture Guide

## System Overview

BEAT SYNC FUNC is built on a modular architecture with four main processing layers:

```
User Input
    ↓
┌─────────────────────────────┐
│   Pipeline Orchestrator     │
└─────────────────────────────┘
    ↓         ↓         ↓         ↓
┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Audio  │ │Video │ │Cutter│ │SVFX  │
│ Layer  │ │Layer │ │Layer │ │Layer │
└────────┘ └──────┘ └──────┘ └──────┘
    ↓         ↓         ↓         ↓
┌─────────────────────────────┐
│   Rendering Engine          │
└─────────────────────────────┘
    ↓
Output Video
```

## Layer Descriptions

### 1. Audio Layer
**Responsible for:** Audio analysis and feature extraction

**Components:**
- `AudioLoader`: Loads and preprocesses audio files
- `BeatDetector`: Detects beats and tempo
- `SpectralAnalyzer`: Analyzes frequency content
- `TurntablismDetector`: Detects scratching and effects

**Key Features:**
- Beat tracking with confidence scores
- Spectral feature extraction (MFCC, chroma)
- Turntablism/scratching detection
- Energy curve generation

### 2. Video Layer
**Responsible for:** Video processing and feature extraction

**Components:**
- `VideoLoader`: Loads video files from pool
- `VideoAnalyzer`: Extracts visual features
- `MotionDetector`: Analyzes motion patterns
- `SceneDetector`: Identifies scene changes

**Key Features:**
- Motion analysis per frame
- Color histogram extraction
- Scene complexity scoring
- Energy level classification

### 3. Cutter Layer (Director Engine)
**Responsible for:** Intelligent cutting decisions and timeline generation

**Components:**
- `Director`: Makes cutting decisions
- `PatternLibrary`: Cut pattern templates
- `TimelineGenerator`: Creates segment timeline

**Key Features:**
- Beat-aligned cutting
- Semantic clip selection
- Pattern matching
- Adaptive learning

### 4. SVFX Layer (Special Visual Effects)
**Responsible for:** Effect composition and rendering

**Components:**
- `EffectComposer`: Composes effect chains
- `TransitionEngine`: Manages transitions
- `SpatialEffects`: Zoom, pan, warp effects
- `TemporalEffects`: Speed, time warp effects

**Key Features:**
- Beat-synced effects
- Smooth blending
- Visual scratching
- Effect composition

## Data Flow

### 1. Loading Phase
```
Input Files
├── Music (MP3/WAV)
└── Clips (MP4/AVI/MOV)
    ↓
Audio/Video Loaders
```

### 2. Analysis Phase
```
Loaded Media
├── Audio Analysis → Beat Times, Spectral Features
└── Video Analysis → Motion Scores, Color Features
    ↓
Feature Vectors
```

### 3. Timeline Generation Phase
```
Feature Vectors + Beats
    ↓
Director Engine
├── Beat Alignment Analysis
├── Semantic Matching
└── Pattern Application
    ↓
Timeline with Segments
```

### 4. Effect Composition Phase
```
Timeline + Beats
    ↓
Effect Composer
├── Transitions
├── Beat-Synced Effects
├── Spatial Effects
└── Temporal Effects
    ↓
Effect Chain
```

### 5. Rendering Phase
```
Clips + Timeline + Effects + Audio
    ↓
FFmpeg Rendering Engine
    ↓
Final Video Output
```

## Configuration

Configuration is managed through YAML files in `config/`:

```yaml
audio:
  sample_rate: 44100
  beat_detector: essentia
video:
  fps: 30
  resolution: [1920, 1080]
cutter:
  min_cut_duration: 0.5
effects:
  effect_intensity: 1.0
```

## Extension Points

### Adding a New Effect
1. Create effect class in `effects/`
2. Implement `apply()` method
3. Register in `EffectComposer`

### Adding a New Beat Detector
1. Implement `detect()` method
2. Add to configuration options
3. Update `BeatDetector` factory

### Custom Cut Patterns
1. Define pattern in `cutter/patterns.py`
2. Add metadata (energy, timing, etc.)
3. Register in `Director`

## Performance Considerations

- Frame sampling (not analyzing every frame)
- GPU acceleration for heavy computation
- Parallel processing of clips
- Caching of computed features
- Memory-efficient streaming for rendering

## Future Enhancements

- Machine learning model for intelligent clip selection
- Real-time preview rendering
- GPU-accelerated effect composition
- Audio-reactive visual generation
- Multi-track audio support